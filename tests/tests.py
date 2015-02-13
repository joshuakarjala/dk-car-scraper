from dk_car_scraper.scraper import get_car_details


def test():
    car_details = get_car_details("AD14219", details=True)

    try:
        assert type(car_details["insurance_company"]) == unicode
        assert type(car_details["car_make"]) == unicode
        assert type(car_details["car_version"]) == unicode
        assert type(car_details["insurance_active"]) == bool
        assert type(car_details["gasoline_type"]) == unicode
        assert type(car_details["year"]) == unicode
        assert type(car_details["car_model"]) == unicode
        assert type(car_details["mileage_per_liter"]) == float

        if car_details["car_purpose"]:
            assert type(car_details["car_purpose"]) == unicode

        if car_details["car_mileage"]:
            assert type(car_details["car_mileage"]) == int

        if car_details["car_type"]:
            assert type(car_details["car_type"]) == unicode

        if car_details["last_update"]:
            assert type(car_details["last_update"]) == unicode

        if car_details["max_passengers"]:
            assert type(car_details["max_passengers"]) == int
    except KeyError, err:
        raise err
