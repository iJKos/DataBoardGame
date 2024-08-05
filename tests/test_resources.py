import pytest
from DataBoardGame.resources import Resources, ResourceType, ResourceConvertion, ResourceScale

def test_resources_addition():
    res1 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res2 = Resources(raw_data=5, marts=3, dashboards=2, insights=4, money=10)
    res3 = res1 + res2
    assert res3.raw_data == 15
    assert res3.marts == 8
    assert res3.dashboards == 5
    assert res3.insights == 12
    assert res3.money == 30

def test_resources_subtraction():
    res1 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res2 = Resources(raw_data=5, marts=3, dashboards=2, insights=4, money=10)
    res3 = res1 - res2
    assert res3.raw_data == 5
    assert res3.marts == 2
    assert res3.dashboards == 1
    assert res3.insights == 4
    assert res3.money == 10

def test_resources_iadd():
    res1 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res2 = Resources(raw_data=5, marts=3, dashboards=2, insights=4, money=10)
    res1 += res2
    assert res1.raw_data == 15
    assert res1.marts == 8
    assert res1.dashboards == 5
    assert res1.insights == 12
    assert res1.money == 30

def test_resources_isub():
    res1 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res2 = Resources(raw_data=5, marts=3, dashboards=2, insights=4, money=10)
    res1 -= res2
    assert res1.raw_data == 5
    assert res1.marts == 2
    assert res1.dashboards == 1
    assert res1.insights == 4
    assert res1.money == 10

def test_resources_getitem():
    res = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    assert res[ResourceType.rawdata] == 10
    assert res[ResourceType.datamart] == 5
    assert res[ResourceType.dashboard] == 3
    assert res[ResourceType.insight] == 8
    assert res[ResourceType.money] == 20

def test_resources_setitem():
    res = Resources()
    res[ResourceType.rawdata] = 10
    res[ResourceType.datamart] = 5
    res[ResourceType.dashboard] = 3
    res[ResourceType.insight] = 8
    res[ResourceType.money] = 20
    assert res.raw_data == 10
    assert res.marts == 5
    assert res.dashboards == 3
    assert res.insights == 8
    assert res.money == 20

def test_resources_comparison():
    res1 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res2 = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res3 = Resources(raw_data=5, marts=3, dashboards=2, insights=4, money=10)
    assert res1 == res2
    assert res1 != res3
    assert res3 < res1
    assert res3 <= res1
    assert res1 > res3
    assert res1 >= res3

def test_resources_to_dict():
    res = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    res_dict = res.to_dict()
    expected_dict = {
        'raw_data': 10,
        'marts': 5,
        'dashboards': 3,
        'insights': 8,
        'money': 20
    }
    assert res_dict == expected_dict

def test_apply_resource_conversion():
    res = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    conversion = ResourceConvertion(
        resources_to_take=Resources(raw_data=2, marts=1, dashboards=1, insights=2, money=5),
        resource_to_give=Resources(raw_data=1, marts=2, dashboards=0, insights=1, money=3)
    )
    res.apply_resource_conversion(conversion)
    assert res.raw_data == 9
    assert res.marts == 6
    assert res.dashboards == 2
    assert res.insights == 7
    assert res.money == 18

def test_apply_resource_scale():
    res = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    scale = ResourceScale(
        resources_to_scale_from=ResourceType.insight,
        scale=0.5,
        resource_to_scale=ResourceType.money
    )
    res.apply_resource_scale(scale)
    assert res.money == 24  # 8 insights * 0.5 = 4 additional money

def test_check_pay_aval():
    res = Resources(raw_data=10, marts=5, dashboards=3, insights=8, money=20)
    conversion = ResourceConvertion(
        resources_to_take=Resources(raw_data=5, marts=2, dashboards=1, insights=4, money=10),
        resource_to_give=Resources()
    )
    assert res.check_pay_aval(conversion) is True

    conversion = ResourceConvertion(
        resources_to_take=Resources(raw_data=15, marts=2, dashboards=1, insights=4, money=10),
        resource_to_give=Resources()
    )
    assert res.check_pay_aval(conversion) is False