from architecto.features.memory.identity import DEFAULT_PROJECT, resolve_project
from architecto.features.memory.ranking import reciprocal_rank_fusion


def test_resolve_project_priorite_slug():
    assert resolve_project("erp", "thread-1") == "erp"
    assert resolve_project("  erp  ", None) == "erp"


def test_resolve_project_repli_thread_puis_default():
    assert resolve_project("", "thread-1") == "thread-1"
    assert resolve_project(None, "  t  ") == "t"
    assert resolve_project(None, None) == DEFAULT_PROJECT
    assert resolve_project("   ", "  ") == DEFAULT_PROJECT


def test_rrf_liste_unique_preserve_ordre():
    assert reciprocal_rank_fusion([["a", "b", "c"]]) == ["a", "b", "c"]


def test_rrf_favorise_les_items_bien_classes_partout():
    semantic = ["d1", "d2", "d3"]
    recency = ["d3", "d1", "d4"]
    fused = reciprocal_rank_fusion([semantic, recency])
    # d1 : rang1 + rang2 ; d3 : rang3 + rang1 -> d1 devant d3 ; tous présents
    assert fused[0] == "d1"
    assert set(fused) == {"d1", "d2", "d3", "d4"}
    assert fused.index("d1") < fused.index("d2")


def test_rrf_item_present_dans_les_deux_bat_item_unique():
    fused = reciprocal_rank_fusion([["x", "y"], ["x", "z"]])
    assert fused[0] == "x"  # x apparaît dans les deux -> score cumulé
