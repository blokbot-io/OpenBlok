# System File

The system file stores the configuration for OpenPod. The base file is created on install and located at `/opt/OpenPod/system.json'. It can easily be accessed by using ob_system.py found in the bloks.

## System File Structure

```JSON
{
    "serial": str,
    "timezone": str,
    "url": str,
    "version": str,
    "debug": bool,
    "models": {
        "location": {
            "version": str,
        },
        "e2e": {
            "version": str,
        }
    },
    "storage":{
        "local": {
            "path": str,
            "maxSizeGB": int,
            "enabled": bool,
        },
        "bucket": {
            "url": str,
            "accessId": str,
            "accessKey": str,
        }
    }
}
```

| Key                      | Type | Description                             |
|--------------------------|------|-----------------------------------------|
| serial                   | str  | The serial number of the pod.           |
| timezone                 | str  | The timezone of the pod.                |
| url                      | str  | The url of the pod.                     |
| version                  | str  | The version of the pod.                 |
| debug                    | bool | The debug mode of the pod.              |
| models                   | dict | The models of the pod.                  |
| models.location          | dict | The location model of the pod.          |
| models.location.version  | str  | The version of the location model.      |
| models.e2e               | dict | The e2e model of the pod.               |
| models.e2e.version       | str  | The version of the e2e model.           |
| storage                  | dict | The storage of the pod.                 |
| storage.local            | dict | The local storage of the pod.           |
| storage.local.path       | str  | The path of the local storage.          |
| storage.local.maxSizeGB  | int  | The max size of the local storage.      |
| storage.local.enabled    | bool | The enabled state of the local storage. |
| storage.bucket           | dict | The bucket storage of the pod.          |
| storage.bucket.url       | str  | The url of the bucket storage.          |
| storage.bucket.accessId  | str  | The access id of the bucket storage.    |
| storage.bucket.accessKey | str  | The access key of the bucket storage.   |
