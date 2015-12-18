Take Home Code Test
===================

Implement a REST service using a python web framework such as flask or django that can be used to store, fetch, and update user records. A user record can be represented in a JSON hash like so:

```json
{
    "first_name": "Joe",
    "last_name": "Smith",
    "userid": "jsmith",
    "groups": ["admins", "users"]
}
```


The service should provide the following endpoints and semantics:

```
GET /users/<userid>
    Returns the matching user record or 404 if none exist.
```

```
POST /users
    Creates a new user record. The body of the request should be a valid user
    record. POSTs to an existing user should be treated as errors and flagged
    with the appropriate HTTP status code.
```

```
DELETE /users/<userid>
    Deletes a user record. Returns 404 if the user doesn't exist.
```

```
PUT /users/<userid>
    Updates an existing user record. The body of the request should be a valid
    user record. PUTs to a non-existant user should return a 404.
```

```
GET /groups/<group name>
    Returns a JSON list of userids containing the members of that group. Should
    return a 404 if the group doesn't exist.
```

```
POST /groups
    Creates a empty group. POSTs to an existing group should be treated as
    errors and flagged with the appropriate HTTP status code. The body should contain
    a `name` parameter
```

```
PUT /groups/<group name>
    Updates the membership list for the group. The body of the request should 
    be a JSON list describing the group's members.
```

```
DELETE /groups/<group name>
    Deletes a group.
```

Implementation Notes:

1. Any design decisions not specified herein are fair game. Completed projects will be evaluated on how closely they follow the spec, their design, and cleanliness of implementation.

2. Completed projects must include a README with enough instructions for evaluators to build and run the code. Bonus points for builds which require minimal manual steps.

3. Remember this project should take a maximum of 8 hours to complete. Do not get hung up on scaling or persistence issues. This is a project used to evaluate your design and implementation skills only.

4. Please include any unit or integration tests used to verify correctness.
