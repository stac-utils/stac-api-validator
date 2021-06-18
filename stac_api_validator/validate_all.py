from validations import validate_api
import traceback


roots = [
    'https://earth-search.aws.element84.com/v0',
    'https://planetarycomputer.microsoft.com/api/stac/v1/',
    'https://eod-catalog-svc-prod.astraea.earth/',
    'https://services.sentinel-hub.com/api/v1/catalog/',
    'https://earthengine.openeo.org/v1.0',
    'https://franklin.nasa-hsi.azavea.com/',
    'https://tamn.snapplanet.io/',
    'https://cmr.earthdata.nasa.gov/stac/LARC_ASDC',
]

for root in roots:
    try:
        print(f"Validating {root} ...", flush=True)

        (warnings, errors) = validate_api(root)

        print(f"warnings:")
        for warning in warnings:
            print(warning)
        print(f"errors:")
        for error in errors:
            print(error)

        if not warnings and not errors:
            print("Valid! 🎉🎉🎉")

        print("---------------------------------------------------")
    except Exception as e:
        print(f"fail.\nError {root}: {type(e)} {str(e)}")
        traceback.print_exc()
