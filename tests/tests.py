from nose.tools import assert_raises

from dk_car_scraper.scraper import get_car_details


def test():
    car_details = get_car_details("AD 14 219", details=True)

    try:
        assert type(car_details["insurance_company"]) == unicode
        assert type(car_details["car_make"]) == unicode
        assert type(car_details["car_version"]) == unicode
        assert type(car_details["insurance_active"]) == bool
        assert type(car_details["gasoline_type"]) == unicode
        assert type(car_details["year"]) == unicode
        assert type(car_details["car_model"]) == unicode
        assert type(car_details["mileage"]) == float

        if car_details["max_passengers"]:
            assert type(car_details["max_passengers"]) == int
    except KeyError, err:
        raise err
