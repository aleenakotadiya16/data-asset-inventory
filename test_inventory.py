import datetime as dt

from inventory import AS_OF, build_database, metrics


def test_catalog_metrics_are_stable():
    path = build_database()
    result = metrics(path)
    assert result["assets"] == 24
    assert result["as_of"] == AS_OF.isoformat()
    assert result["percent_classified"] == 87.5
    assert result["missing_owner"] == 3
    assert result["percent_without_owner"] == 12.5
    assert result["expired_agreements"] == 11
    assert result["with_agreement"] == 18
    assert result["percent_agreements_expired"] == 61.1
    assert AS_OF == dt.date(2026, 11, 6)
