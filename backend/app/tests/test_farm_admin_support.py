from app.main import app
from app.modules.farms.schemas import (
    AdminFarmAuditOut,
    AdminFarmCycleSummaryOut,
    AdminFarmPlotSummaryOut,
    AdminFarmSummaryOut,
)


def test_admin_farm_routes_are_read_only_and_registered() -> None:
    methods_by_path = {
        path: {method.upper() for method in operations}
        for path, operations in app.openapi()["paths"].items()
        if path.startswith("/api/v1/admin/farms")
    }

    assert methods_by_path == {
        "/api/v1/admin/farms": {"GET"},
        "/api/v1/admin/farms/{farm_id}": {"GET"},
        "/api/v1/admin/farms/{farm_id}/audit": {"GET"},
    }


def test_admin_farm_contract_excludes_private_farm_data() -> None:
    exposed = (
        set(AdminFarmSummaryOut.model_fields)
        | set(AdminFarmPlotSummaryOut.model_fields)
        | set(AdminFarmCycleSummaryOut.model_fields)
        | set(AdminFarmAuditOut.model_fields)
    )

    assert exposed.isdisjoint(
        {
            "latitude",
            "longitude",
            "boundary_geojson",
            "notes",
            "result_value",
            "media",
            "storage_key",
        }
    )
