# Candidate Service

This service is responsible for managing candidates, applications, and profiles.

## How to Test

To run the tests for this service, you will need to have `pytest` installed. The tests are located in the `tests/` directory.

To run the tests, execute the following command from the root of the repository:

```bash
pytest services/candidate-service/tests/
```

The tests use FastAPI's `TestClient` to run in-process, so there is no need to run a live server.
