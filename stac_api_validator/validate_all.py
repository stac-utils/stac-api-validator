from validations import validate_api

roots = [ 
    'https://earth-search.aws.element84.com/v0',
    'https://planetarycomputer.microsoft.com/api/stac/v1/',
    'https://eod-catalog-svc-prod.astraea.earth/',
    'https://services.sentinel-hub.com/api/v1/catalog/',
    'https://api.radiant.earth/mlhub/v1/',
    'https://earthengine.openeo.org/v1.0',
    'https://franklin.nasa-hsi.azavea.com/',
    'https://tamn.snapplanet.io/',
    'https://data.geo.admin.ch/api/stac/v0.9/',
    'https://cmr.earthdata.nasa.gov/stac/LARC_ASDC',
    'https://landsatlook.usgs.gov/sat-api/stac'
 ]

for root in roots:
    try:
        print(f"Validating {root} ...", flush=True)

        (errors, warnings) = validate_api(root)

        print(f"warnings: {warnings}")
        print(f"errors: {errors}")

        if not warnings and not errors:
            print("valid!")
    except Exception as e:
        print(f"fail.\nError {root}: {type(e)} {str(e)}")
