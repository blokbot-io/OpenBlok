## Raw

```JSON
{
    "frame": byte,
    "metadata": {
        "timestamp": float,
        "rawUUID": str
    }
}
```

## Rotated

```JSON
{
    "frame": byte,
    "metadata": {
        "timestamp": float,
        "rawUUID": str,
        "rotatedUUID": str,
        "rotationCorrection": {
            "arucoCenterX": int,
            "arucoCenterY": int,
            "angleOffset": float
        }
    }
}
```

## ROI

```JSON
{
    "frame": byte,
    "metadata": {
        "timestamp": float,
        "rawUUID": str,
        "rotatedUUID": str,
        "roiUUID": str,
        "rotationCorrection": {
            "arucoCenterX": int,
            "arucoCenterY": int,
            "angleOffset": float
        },
        "roi": {
            "topView": {
                "upperLeft": [],
                "lowerRight": []
            },
            "sideView": {
                "upperLeft": [],
                "lowerRight": []
            }
        }
    }
}
```

## Predicted

```JSON
{
    "frame": byte,
    "metadata": {
        "timestamp": float,
        "rawUUID": str,
        "rotatedUUID": str,
        "roiUUID": str,
        "predictedUUID": str,
        "rotationCorrection": {
            "arucoCenterX": int,
            "arucoCenterY": int,
            "angleOffset": float
        },
        "roi": {
            "topView": {
                "upperLeft": [],
                "lowerRight": []
            },
            "sideView": {
                "upperLeft": [],
                "lowerRight": []
            },
            "inferences": {
                "location": {
                    "topMidpoint": [],
                    "sideMidpoint": [],
                    "crop":{
                        "topView": {
                            "upperLeft": [],
                            "lowerRight": []
                        },
                        "sideView": {
                            "upperLeft": [],
                            "lowerRight": []
                        }
                    }
                },
                "e2e": {
                    "design": [],
                    "category": []
                }
            }
        }
    }
}
```
