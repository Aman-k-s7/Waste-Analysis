import json

from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from analytics.services.chat import answer_dashboard_question
from analytics.services.dashboard import (
    get_anomaly_days,
    get_daily_waste_trend,
    get_dashboard_summary,
    get_dashboard_insights,
    get_filter_options,
    get_moisture_data,
    get_reason_breakdown,
    get_top_devices,
    get_waste_by_food_item,
    get_waste_by_meal,
    get_waste_by_weekday,
    get_weekday_comparison_grid,
    get_waste_by_category,
    get_weekly_waste,
    get_usage_analytics,
    get_bain_marie_analytics,
    get_daily_avg_by_category,
)
from analytics.services.filters import FilterParams, parse_filters


def _parse_request_filters(request: HttpRequest) -> FilterParams:
    return parse_filters(request.GET)


def _normalize_chat_filters(raw_filters: dict) -> dict:
    normalized = dict(raw_filters or {})
    if "dateFrom" in normalized and "date_from" not in normalized:
        normalized["date_from"] = normalized.get("dateFrom")
    if "dateTo" in normalized and "date_to" not in normalized:
        normalized["date_to"] = normalized.get("dateTo")
    if "mealTypes" in normalized and "meal_types" not in normalized:
        value = normalized.get("mealTypes")
        normalized["meal_types"] = ",".join(value) if isinstance(value, list) else value
    if "wasteTypes" in normalized and "waste_types" not in normalized:
        value = normalized.get("wasteTypes")
        normalized["waste_types"] = ",".join(value) if isinstance(value, list) else value
    if "weeks" in normalized:
        value = normalized.get("weeks")
        if isinstance(value, list):
            normalized["weeks"] = ",".join(value)
    for key in ("devices", "categories"):
        value = normalized.get(key)
        if isinstance(value, list):
            normalized[key] = ",".join(value)
    return normalized


def _invalid_filters_response(exc: ValidationError) -> JsonResponse:
    return JsonResponse({"errors": exc.message_dict if hasattr(exc, "message_dict") else exc.messages}, status=400)


def _database_error_response(exc: DatabaseError) -> JsonResponse:
    return JsonResponse(
        {
            "errors": [
                "Database query failed. Confirm the imported MySQL schema and the WASTE_* column/table settings.",
                str(exc),
            ]
        },
        status=500,
    )


@require_GET
def dashboard_summary(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_dashboard_summary(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@require_GET
def waste_by_category(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_waste_by_category(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def waste_by_food_item(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_waste_by_food_item(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def waste_by_meal(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_waste_by_meal(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def daily_waste_trend(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_daily_waste_trend(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def anomaly_days(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_anomaly_days(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def weekly_waste(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_weekly_waste(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def waste_by_weekday(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_waste_by_weekday(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def weekday_comparison_grid(request: HttpRequest) -> JsonResponse:
    try:
        filters = _parse_request_filters(request)
        weeks = [week.strip() for week in (request.GET.get("weeks") or "").split(",") if week.strip()]
        payload = get_weekday_comparison_grid(filters, weeks)
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@require_GET
def top_devices(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_top_devices(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def dashboard_insights(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_dashboard_insights(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@require_GET
def filter_options(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_filter_options()
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@csrf_exempt
@require_http_methods(["POST"])
def chat_query(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"errors": ["Invalid JSON body."]}, status=400)

    question = (payload.get("question") or "").strip()
    provider = (payload.get("provider") or "local").strip().lower()
    if not question:
        return JsonResponse({"errors": ["Question is required."]}, status=400)

    try:
        filters = parse_filters(_normalize_chat_filters(payload.get("filters") or {}))
        answer = answer_dashboard_question(question, filters, provider=provider)
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)

    return JsonResponse(answer)


@require_GET
def debug_scan_count(request: HttpRequest) -> JsonResponse:
    """Temporary diagnostic endpoint — remove after investigation."""
    from django.db import connection as _conn
    import os as _os
    table = _os.getenv("WASTE_SCAN_TABLE", "scm_scans")
    company = int(_os.getenv("WASTE_COMPANY_ID", "312"))
    devices = ("AGFW26010", "CFSO13")
    ph = ", ".join(["%s"] * len(devices))
    results = {}
    with _conn.cursor() as c:
        # 1. Total with current filters (is_valid=1, commodity, date)
        try:
            c.execute(
                f"SELECT COUNT(*) FROM `{table}` WHERE company_id=%s AND is_valid=1"
                f" AND commodity_name IS NOT NULL AND created_on_date IS NOT NULL"
                f" AND device_serial_no IN ({ph})",
                [company, *devices]
            )
            results["count_is_valid_1"] = c.fetchone()[0]
        except Exception as e:
            results["count_is_valid_1"] = f"ERROR: {e}"

        # 2. Total without is_valid filter
        try:
            c.execute(
                f"SELECT COUNT(*) FROM `{table}` WHERE company_id=%s"
                f" AND commodity_name IS NOT NULL AND created_on_date IS NOT NULL"
                f" AND device_serial_no IN ({ph})",
                [company, *devices]
            )
            results["count_no_is_valid"] = c.fetchone()[0]
        except Exception as e:
            results["count_no_is_valid"] = f"ERROR: {e}"

        # 3. Check if is_valid column exists
        try:
            c.execute(
                f"SELECT COUNT(*) FROM `{table}` WHERE company_id=%s AND device_serial_no IN ({ph}) AND is_valid IS NOT NULL LIMIT 1",
                [company, *devices]
            )
            results["is_valid_column_exists"] = True
        except Exception:
            results["is_valid_column_exists"] = False

        # 4. Rows on May 25 with is_valid != 1
        try:
            c.execute(
                f"SELECT id, device_serial_no, is_valid, commodity_name, weight, created_on_date"
                f" FROM `{table}` WHERE company_id=%s AND device_serial_no IN ({ph})"
                f" AND created_on_date='2026-05-25'",
                [company, *devices]
            )
            cols = [d[0] for d in c.description]
            results["may25_rows"] = [dict(zip(cols, row)) for row in c.fetchall()]
        except Exception as e:
            results["may25_rows"] = f"ERROR: {e}"

    return JsonResponse(results)


@require_GET
def reason_breakdown(request: HttpRequest) -> JsonResponse:
    try:
        filters = _parse_request_filters(request)
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    category = request.GET.get("category", "").strip()
    try:
        payload = get_reason_breakdown(filters, category=category)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def moisture_data(request: HttpRequest) -> JsonResponse:
    try:
        filters = _parse_request_filters(request)
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    limit = request.GET.get("limit")
    try:
        payload = get_moisture_data(filters, limit=int(limit) if limit and limit.isdigit() else 250)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)


@require_GET
def usage_analytics(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_usage_analytics(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@require_GET
def bain_marie_analytics(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_bain_marie_analytics(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload)


@require_GET
def daily_avg_by_category(request: HttpRequest) -> JsonResponse:
    try:
        payload = get_daily_avg_by_category(_parse_request_filters(request))
    except ValidationError as exc:
        return _invalid_filters_response(exc)
    except DatabaseError as exc:
        return _database_error_response(exc)
    return JsonResponse(payload, safe=False)
