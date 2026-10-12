from retrieval.hybrid_retriever import search_hybrid


def test_english_rural_roads_retrieves_tnrris():
    results = search_hybrid(
        "Which scheme improves village roads and rural connectivity?",
        limit=5,
    )
    scheme_names = [item["scheme_name"] for item in results]

    assert any("TNRRIS" in name for name in scheme_names), (
        f"Expected TNRRIS in results, got: {scheme_names}"
    )


def test_unconnected_habitations_retrieves_tnrris():
    results = search_hybrid(
        "Which scheme provides roads connecting unconnected rural habitations?",
        limit=5,
    )
    scheme_names = [item["scheme_name"] for item in results]

    assert any("TNRRIS" in name for name in scheme_names), (
        f"Expected TNRRIS in results, got: {scheme_names}"
    )

def test_tamil_rural_roads_retrieval():
    results = search_hybrid(
        "கிராமப்புற சாலைகளை மேம்படுத்தும் திட்டம் எது?",
        limit=5,
    )

    scheme_names = [item["scheme_name"] for item in results]

    print("\nTamil question retrieved schemes:", scheme_names)

    assert any("TNRRIS" in name for name in scheme_names), (
        f"Expected TNRRIS in Tamil query results, got: {scheme_names}"
    )
