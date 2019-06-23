Requirements for the request:
- Content-Type of request is application/json;
- all parameters that are integer in db should be integer in json.

Methods:
1) URL: "/limits", method: GET
Response code: 200
Returns json with all limits, like:
[
    {
        "id": 1,
        "country": "AUS",
        "currency": "USD",
        "max_per_month": 100000
    },
    {
        "id": 2,
        "country": "RUS",
        "currency": "RUB",
        "max_per_month": 3500000
    }
]

2) URL: "/limits/id_record", method: GET
Response code: 200 (success), 404 (resource doesn't exist)
Returns json with limit's data, like:
{
    "id": 1,
    "country": "AUS",
    "currency": "USD",
    "max_per_month": 100000
}

3) URL: "/limits", method: POST
Response codes: 201 (success), 400 (problems with incoming parameters), 422 (problems with values of incoming parameters plus below *)
Returns json with new limit's data, like:
{
    "id": 6,
    "country": "RUS",
    "currency": "EUR",
    "max_per_month": 150000
}
* If client app tries to create a record with existed combination "country"-"currency" the method returns 422 Response.
There can't be another record with this direction of transfer.

4) URL: "/limits/id_record", method: PUT
Response codes: 204 (success), 404 (resource doesn't exist), 400 (problems with incoming parameters),
422 (problems with values of incoming parameters plus **)
Returns empty json.
** If client app tries to change record, and other record has incoming combination "country"-"currency" the method returns 422 Response.
There can't be another record with this direction of transfer.

5) URL: "/limits/id_record", method: DELETE
Response codes: 204 (success), 404 (resource doesn't exist)
Returns empty json.

6) URL: "/payments", method: GET
Response code: 200
Returns json with full history of transfers, like:
[
    {
        "id": 1,
        "id_client": 4511,
        "date_transfer": "2019-04-07 20:08:03",
        "transfer_amount": 45000,
        "currency": "RUB",
        "country": "ABH"
    },
    {
        "id": 2,
        "id_client": 4328,
        "date_transfer": "2019-04-14 10:02:41",
        "transfer_amount": 7800,
        "currency": "USD",
        "country": "RUS"
    }
]

7) URL: "/payments/id_record", method: GET
Response code: 200 (success), 404 (resource doesn't exist)
Returns json with transfer's data, like:
{
    "id": 1,
    "id_client": 4511,
    "date_transfer": "2019-04-07 20:08:03",
    "transfer_amount": 45000,
    "currency": "RUB",
    "country": "ABH"
}

8) URL: "/payments", method: POST
Response codes: 201 (success), 400 (problems with incoming parameters), 422 (problems with values of incoming parameters plus below ***)
Returns json with new transfer's data, like:
{
    "id": 8,
    "id_client": 4541,
    "date_transfer": "2019-04-29 13:52:32",
    "transfer_amount": 5000,
    "currency": "RUB",
    "country": "ABH"
}
*** If client app tries to create record with a non-existed combination "country"-"currency" the method returns 422 Response.
There can't be a transfer in non-existed direction.
**** If total transfer's amount of the money (from the new record and other records in current month) oversteps the limit in this direction the method returns 422 Response.

