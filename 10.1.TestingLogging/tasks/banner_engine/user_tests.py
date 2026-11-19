from typing import Any
from unittest.mock import patch

import pytest

import banner_engine
from banner_engine import BannerStat, Banner, BannerStorage, EpsilonGreedyBannerEngine, EmptyBannerStorageError

TEST_DEFAULT_CTR = 0.1


@pytest.fixture(scope="function")
def test_banners() -> list[Banner]:
    return [
        Banner("b1", cost=1, stat=BannerStat(10, 20)),
        Banner("b2", cost=250, stat=BannerStat(20, 20)),
        Banner("b3", cost=100, stat=BannerStat(0, 20)),
        Banner("b4", cost=100, stat=BannerStat(1, 20)),
    ]


@pytest.mark.parametrize("clicks, shows, expected_ctr", [(1, 1, 1.0), (20, 100, 0.2), (5, 100, 0.05)])
def test_banner_stat_ctr_value(clicks: int, shows: int, expected_ctr: float) -> None:
    stat = BannerStat(clicks, shows)
    assert stat.compute_ctr(TEST_DEFAULT_CTR) == expected_ctr


def test_empty_stat_compute_ctr_returns_default_ctr() -> None:
    stat = BannerStat(0, 0)
    assert stat.compute_ctr(TEST_DEFAULT_CTR) == TEST_DEFAULT_CTR


def test_banner_stat_add_show_lowers_ctr() -> None:
    stat = BannerStat(10, 20)
    initial_ctr = stat.compute_ctr(TEST_DEFAULT_CTR)
    stat.add_show()
    new_ctr = stat.compute_ctr(TEST_DEFAULT_CTR)
    assert new_ctr < initial_ctr


def test_banner_stat_add_click_increases_ctr() -> None:
    stat = BannerStat(10, 20)
    initial_ctr = stat.compute_ctr(TEST_DEFAULT_CTR)
    stat.add_click()
    new_ctr = stat.compute_ctr(TEST_DEFAULT_CTR)
    assert new_ctr > initial_ctr


def test_get_banner_with_highest_cpc_returns_banner_with_highest_cpc(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    best_banner = storage.banner_with_highest_cpc()

    best_cpc = best_banner.stat.compute_ctr(TEST_DEFAULT_CTR) * best_banner.cost
    for banner in test_banners:
        cpc = banner.stat.compute_ctr(TEST_DEFAULT_CTR) * banner.cost
        assert cpc <= best_cpc


def test_banner_engine_raise_empty_storage_exception_if_constructed_with_empty_storage() -> None:
    empty_storage = BannerStorage([])
    with pytest.raises(EmptyBannerStorageError):
        EpsilonGreedyBannerEngine(empty_storage, 0.1)


def test_engine_send_click_not_fails_on_unknown_banner(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 0.1)
    engine.send_click("unknown_banner")


def test_engine_with_zero_random_probability_shows_banner_with_highest_cpc(
    test_banners: list[Banner], monkeypatch: Any = None
) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 0.0)

    best_banner = storage.banner_with_highest_cpc()

    if monkeypatch is not None:
        monkeypatch.setattr(banner_engine.random, "random", lambda: 1.0)
        shown_banner_id = engine.show_banner()
    else:
        with patch.object(banner_engine.random, "random", return_value=1.0):
            shown_banner_id = engine.show_banner()

    assert shown_banner_id == best_banner.banner_id


@pytest.mark.parametrize("expected_random_banner", ["b1", "b2", "b3", "b4"])
def test_engine_with_1_random_banner_probability_gets_random_banner(
    expected_random_banner: str, test_banners: list[Banner], monkeypatch: Any = None
) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 1.0)

    def mock_choice(items):
        return expected_random_banner

    if monkeypatch is not None:
        monkeypatch.setattr(banner_engine.random, "random", lambda: 0.5)
        monkeypatch.setattr(banner_engine.random, "choice", mock_choice)
        shown_banner_id = engine.show_banner()
    else:
        with patch.object(banner_engine.random, "random", return_value=0.5), \
             patch.object(banner_engine.random, "choice", side_effect=mock_choice):
            shown_banner_id = engine.show_banner()
    assert shown_banner_id == expected_random_banner


def test_total_cost_equals_to_cost_of_clicked_banners(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 0.0)

    total_expected_cost = 0
    for banner in test_banners:
        engine.send_click(banner.banner_id)
        total_expected_cost += banner.cost

    assert engine.total_cost == total_expected_cost


def test_engine_show_increases_banner_show_stat(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 0.0)

    initial_shows = {b.banner_id: b.stat.shows for b in test_banners}

    with patch.object(banner_engine.random, "random", return_value=0.0):
        shown_banner_id = engine.show_banner()

    for banner in test_banners:
        if banner.banner_id == shown_banner_id:
            assert banner.stat.shows == initial_shows[banner.banner_id] + 1
        else:
            assert banner.stat.shows == initial_shows[banner.banner_id]


def test_engine_click_increases_banner_click_stat(test_banners: list[Banner]) -> None:
    storage = BannerStorage(test_banners, TEST_DEFAULT_CTR)
    engine = EpsilonGreedyBannerEngine(storage, 0.0)

    banner = test_banners[0]
    initial_clicks = banner.stat.clicks
    engine.send_click(banner.banner_id)
    assert banner.stat.clicks == initial_clicks + 1
