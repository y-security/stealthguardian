# Developing an Agent
The `Endpoint Agent` observes user-defined logfiles and alerts during the execution of actions to verify if a malicious event has been detected. After execution of the action by the `Middleware`, the `Endpoint Agent` communicates its results back.

The `Agent` may run on a system on which the Beacon is installed, but can also be used to observe logfiles on other systems, e.g. querying `Elasticsearch`.

## Registration

The following steps need to be completed to register an `Agent`to the `Middleware` - In this case we assume that one `Agent` is deployed per system:

1. Send a GET request to `/api/generate-uuid` in order to register a new `Agent` - The server will return a UUID such as `9d33d798-54a0-4f35-af07-a86b6784f404`, which is used as the `Agent` key:

```
curl -X 'GET' \
  'https://stealthguardian-middleware:45134/api/generate-uuid' \
  -H 'accept: application/json'
```

2. Send a POST request to `/api/activate` to provide information about your system and the `Middleware` you communicate with:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/activate' \
  -H 'accept: application/json' \
  -H 'StealthGuardianEndpointAPIKey: 9d33d798-54a0-4f35-af07-a86b6784f404' \
  -H 'Content-Type: application/json' \
  -d '{
  "uuid": "9d33d798-54a0-4f35-af07-a86b6784f404",
  "name": "My system name"
}'
```

3. Finally, you can retrieve the `Agent` configuration via `/api/get-configuration` , which may includes `Scripts` to execute:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/get-configuration' \
  -H 'accept: application/json' \
  -H 'StealthGuardianEndpointAPIKey: 9d33d798-54a0-4f35-af07-a86b6784f404' \
  -H 'Content-Type: application/json' \
  -d '{
  "uuid": "9d33d798-54a0-4f35-af07-a86b6784f404"
}'
```

## Sending Logs
`Agents` can submit logs to the `Middleware`. The `Middleware` accepts `undetected` and `detected` as valid `status` values. The event may also contain additional information about what has been executed, such as the `raw_event`, or `executed_module`:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/agentlogs/add' \
  -H 'accept: application/json' \
  -H 'StealthGuardianEndpointAPIKey: 9d33d798-54a0-4f35-af07-a86b6784f404' \
  -H 'Content-Type: application/json' \
  -d '{
  "agentuuid": "9d33d798-54a0-4f35-af07-a86b6784f404",
  "status": "detected",
  "raw_event": "Found Malicious Event XY",
  "check_type": "auto",
  "module_uuid": "RandomString",
  "executed_module": 1
}'
```

## Receiving Commands
Depending on your use case, you may want to update the `Agent` configuration or send commands to the `Agent`. In order to do so you can query the `api/agenttask/<UUID>` endpoint:

```
curl -X 'GET' \
  'https://stealthguardian-middleware:45134/api/agenttask/9d33d798-54a0-4f35-af07-a86b6784f404' \
  -H 'accept: application/json' \
  -H 'StealthGuardianEndpointAPIKey: 9d33d798-54a0-4f35-af07-a86b6784f404'
```


# Developing an Integration Component
The `Integration` component is the bridge between the adversary simulation tool and the middleware. It forwards executed actions to the `Middleware`.

## Register a Beacon
Beacons can be registered to the middleware and afterwards assigned to reference systems via the UI. In order to register a new Beacon, the following request needs to be send to the `Middleware`:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/beacons/add' \
  -H 'accept: application/json' \
  -H 'StealthGuardianAPIKey: YareyouusingthedefaultkeyY' \
  -H 'Content-Type: application/json' \
  -d '{
  "buid": "MyBeaconUUID",
  "name": "YSoManyBeacons",
  "source": "cobaltstrike"
}'
```

## Add New Tasks
A new `Task` can be registered to the `Middleware` by sending a POST Request to either `/api/tasks/add` or `/api/tasks/add/withfile`. The second one can be used to upload a binary file to the application that can then be processed:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/tasks/add' \
  -H 'accept: application/json' \
  -H 'StealthGuardianAPIKey: YareyouusingthedefaultkeyY' \
  -H 'Content-Type: application/json' \
  -d '{
  "source": "cobaltstrike",
  "sourceBeacon": "MySourceBeaconUUID",
  "targetBeacon": "MyTargetBeaconUUID",
  "command": "shell whoami"
}'
```

## Process Tasks
The `Integration` component also needs to process added `Tasks`.

### Request Outstanding Tasks
In order to retrieve a list of outstanding `Tasks`, the endpoint `/api/tasks/<source>` can be queried

```
curl -X 'GET' \
  'https://stealthguardian-middleware:45134/api/tasks/cobaltstrike' \
  -H 'accept: application/json' \
  -H 'StealthGuardianAPIKey: YareyouusingthedefaultkeyY'
```

The returned entries can then be processed.

### Update Outstanding Tasks
After executing an outstanding `Task` you should update the status to not execute the `Task` again - Depending on your simulation software you may also include the result of the execution:

```
curl -X 'POST' \
  'https://stealthguardian-middleware:45134/api/tasks/update' \
  -H 'accept: application/json' \
  -H 'StealthGuardianAPIKey: YareyouusingthedefaultkeyY' \
  -H 'Content-Type: application/json' \
  -d '{
  "taskid": "2f255589-9fda-4c81-a735-c0e44c467111",
  "status": "executed",
  "result": ""
}'
```

| Status    | Description                                                                                                 |
| --------- | ----------------------------------------------------------------------------------------------------------- |
| queued    | A task was send from the integration layer to the middleware and can be executed against a reference beacon |
| executed  | The tasks was collected from the middleware and send to the reference beacon                                |
| completed | The task was executed against the reference beacon and a response was collected                             |
| notified  | The user has been notified about the result                                                                 |
