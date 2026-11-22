"""Customer report: the dashboard's returned assets appear out of order."""

from upstream import AssetClient


if __name__ == "__main__":
    requested = ["A-100", "A-200", "A-300", "A-100"]
    records = AssetClient().fetch_many(requested)
    actual = [record["id"] if record else None for record in records]
    print("Requested:", requested)
    print("Returned: ", actual)
    print("Order matches:", requested == actual)
