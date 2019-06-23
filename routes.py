from aiohttp import web
from datetime import datetime
from sqlalchemy import func, select

from db import limits, payments
from helper import create_dict, encode, check_params

routes = web.RouteTableDef()


@routes.get("/limits", allow_head=False)
async def get_limits(request):
    engine = request.app['db']
    async with engine.acquire() as conn:
        data = await conn.execute(limits.select())
        data = create_dict(limits.c, data)
    return web.json_response(data, status=200)


@routes.get("/limits/{limit_id:\d+}", allow_head=False)
async def get_limit_record(request):
    engine = request.app['db']
    resource_id = int(request.match_info['limit_id'])
    async with engine.acquire() as conn:
        curr_record_id = await conn.scalar(limits.select().where(limits.c.id == resource_id))
        if curr_record_id:
            curr_record = await conn.execute(limits.select().where(limits.c.id == resource_id))
            data = create_dict(limits.c, curr_record, one_rec=True)
            return web.json_response(data, status=200)

        return web.json_response(status=404)


@routes.post("/limits")
async def add_new_limit(request):
    engine = request.app['db']
    params = await request.json()

    params_validation = check_params(limits.c, params)
    if not params_validation["validated"]:
        return web.json_response({"errors": params_validation["errors"]}, status=params_validation["code"])

    async with engine.acquire() as conn:
        id_other_rec = await conn.scalar(limits.select().where(limits.c.currency == params["currency"])
                                         .where(limits.c.country == params["country"]))
        if id_other_rec:
            message = "Resource with combination (country-currency) already exists. Id of this one: {}".format(
                id_other_rec)
            return web.json_response({"error": message}, status=422)

        record_id = await conn.scalar(limits.insert().values(**params))
        data = await conn.execute(limits.select().where(limits.c.id == record_id))
        data = create_dict(limits.c, data, one_rec=True)

    return web.json_response(data, status=201)


@routes.put("/limits/{limit_id:\d+}")
async def change_limit_record(request):
    engine = request.app['db']
    resource_id = int(request.match_info['limit_id'])

    async with engine.acquire() as conn:
        curr_record = await conn.scalar(limits.select().where(limits.c.id == resource_id))
        if not curr_record:
            return web.json_response(status=404)

    params = await request.json()
    params_validation = check_params(limits.c, params)
    if not params_validation["validated"]:
        return web.json_response({"errors": params_validation["errors"]}, status=params_validation["code"])

    async with engine.acquire() as conn:
        id_other_rec = await conn.scalar(limits.select().where(limits.c.currency == params["currency"])
                                         .where(limits.c.country == params["country"]))
        if id_other_rec and id_other_rec != resource_id:
            message = "Resource with combination (country-currency) already exists. Id of this one: {}".format(
                id_other_rec)
            return web.json_response({"error": message}, status=422)

        await conn.execute(limits.update().where(limits.c.id == resource_id).values(**params))

    return web.json_response(status=204)


@routes.delete("/limits/{limit_id:\d+}")
async def delete_limit_record(request):
    engine = request.app['db']
    resource_id = int(request.match_info['limit_id'])
    async with engine.acquire() as conn:
        curr_record = await conn.scalar(limits.select().where(limits.c.id == resource_id))
        if not curr_record:
            return web.Response(status=404)
        await conn.execute(limits.delete().where(limits.c.id == resource_id))

    return web.json_response(status=204)


@routes.get("/payments", allow_head=False)
async def get_payments(request):
    engine = request.app['db']
    async with engine.acquire() as conn:
        data = await conn.execute(payments.select())
        data = encode(create_dict(payments.c, data))
    return web.Response(status=200, body=data, content_type='application/json')


@routes.get("/payments/{payment_id:\d+}", allow_head=False)
async def get_payment_record(request):
    engine = request.app['db']
    resource_id = int(request.match_info['payment_id'])
    async with engine.acquire() as conn:
        curr_record_id = await conn.scalar(payments.select().where(payments.c.id == resource_id))
        if curr_record_id:
            curr_record = await conn.execute(payments.select().where(payments.c.id == resource_id))
            data = encode(create_dict(payments.c, curr_record, one_rec=True))
            return web.Response(status=200, body=data, content_type='application/json')

        return web.json_response(status=404)



@routes.post("/payments")
async def add_new_payment(request):
    engine = request.app['db']
    params = await request.json()

    params_validation = check_params(payments.c, params)
    if not params_validation["validated"]:
        return web.json_response({"errors": params_validation["errors"]}, status=params_validation["code"])

    date_payment = datetime.strptime(params["date_transfer"], "%Y-%m-%d %H:%M:%S")
    start_month_date = datetime(date_payment.year, date_payment.month, 1, 0, 0, 0)
    end_month_date = datetime(date_payment.year, date_payment.month + 1, 1, 0, 0, 0)

    async with engine.acquire() as conn:
        id_limit_rec = await conn.scalar(limits.select().where(limits.c.currency == params["currency"])
                                         .where(limits.c.country == params["country"]))
        if not id_limit_rec:
            message = "This transfer direction doesn't exist"
            return web.json_response({"error": message}, status=422)

        limit_transfer = await conn.scalar(select([limits.c.max_per_month])
                                           .where(limits.c.currency == params["currency"])
                                           .where(limits.c.country == params["country"]))
        sum_previous_transfers = await conn.scalar(select([func.sum(payments.c.transfer_amount)])
            .where(payments.c.id_client == params["id_client"])
            .where(payments.c.currency == params["currency"])
            .where(payments.c.country == params["country"])
            .where(
            payments.c.date_transfer.between(start_month_date, end_month_date)))

        sum_previous_transfers = sum_previous_transfers if sum_previous_transfers is not None else 0

        total_transfer = sum_previous_transfers + params["transfer_amount"]
        if total_transfer <= limit_transfer:
            record_id = await conn.scalar(payments.insert().values(**params))
            data = await conn.execute(payments.select().where(payments.c.id == record_id))
            data = encode(create_dict(payments.c, data, one_rec=True))
            return web.Response(status=201, body=data, content_type='application/json')
        else:
            message = "The limit of payments in this direction is exceeded"
            return web.json_response({"error": message}, status=422)
