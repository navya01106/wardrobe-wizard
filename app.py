import streamlit as st

import engine

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
st.title("Wardrobe Wizard")
st.caption("Add what you already own and get outfits that match.")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

wardrobe = engine.load("wardrobe")
saved = engine.load("outfits")
by_id = {i["id"]: i for i in wardrobe}


def show_item(item):
    photo = engine.PHOTO_DIR / item["photo"] if item.get("photo") else None
    if photo and photo.exists():
        st.image(str(photo), use_container_width=True)
    else:
        st.markdown(
            f"<div style='height:110px;border-radius:6px;border:1px solid #8884;"
            f"background:{engine.COLORS[item['color']]}'></div>",
            unsafe_allow_html=True,
        )
    st.markdown(f"**{item['name']}**")
    st.caption(f"{item['category']}, {item['color']}")


tab_wardrobe, tab_add, tab_outfits, tab_saved = st.tabs(
    ["Wardrobe", "Add item", "Outfit ideas", "Saved outfits"]
)

with tab_wardrobe:
    if not wardrobe:
        st.info("Your wardrobe is empty. Add an item, or start with a sample set.")
        if st.button("Load sample wardrobe"):
            engine.save("wardrobe", engine.sample_wardrobe())
            st.rerun()
    else:
        show = st.selectbox("Show", ["all"] + engine.CATEGORIES)
        items = [i for i in wardrobe if show == "all" or i["category"] == show]
        cols = st.columns(4)
        for n, item in enumerate(items):
            with cols[n % 4]:
                show_item(item)
                st.caption("Good for " + ", ".join(item["occasions"]))
                if st.button("Remove", key=f"rm_{item['id']}"):
                    engine.remove_item(item["id"])
                    st.rerun()

with tab_add:
    with st.form("add_item", clear_on_submit=True):
        name = st.text_input("Name", placeholder="Blue denim jacket")
        left, right = st.columns(2)
        category = left.selectbox("Type", engine.CATEGORIES)
        color = right.selectbox("Main colour", list(engine.COLORS))
        occasions = st.multiselect("Good for", engine.OCCASIONS, default=["casual"])
        photo = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png"])
        if st.form_submit_button("Add to wardrobe"):
            if not name.strip() or not occasions:
                st.error("Enter a name and pick at least one occasion.")
            else:
                ext = photo.name.rsplit(".", 1)[-1].lower() if photo else None
                engine.add_item(name, category, color, occasions,
                                photo.getvalue() if photo else None, ext)
                st.session_state["flash"] = f"Added {name.strip()}."
                st.rerun()

with tab_outfits:
    c1, c2, c3 = st.columns(3)
    occasion = c1.selectbox("Occasion", engine.OCCASIONS)
    cold = c2.checkbox("It's cold, add outerwear")
    count = c3.slider("How many ideas", 1, 10, 4)
    if st.button("Suggest outfits", type="primary"):
        st.session_state["results"] = engine.generate(wardrobe, occasion, cold, count)
        st.session_state["results_occasion"] = occasion

    results = st.session_state.get("results")
    if results is not None and not results:
        st.warning(
            "No complete outfit found. For this occasion you need a top and a "
            "bottom, or a dress, tagged for it."
        )
    for n, outfit in enumerate(results or []):
        st.divider()
        st.subheader(f"Outfit {n + 1}, match score {outfit['score']}/100")
        cols = st.columns(4)
        for col, piece in zip(cols, outfit["pieces"]):
            with col:
                show_item(piece)
        for note in outfit["notes"]:
            st.write(f"- {note}")
        if st.button("Save outfit", key=f"save_{n}"):
            saved.append({
                "ids": [p["id"] for p in outfit["pieces"]],
                "score": outfit["score"],
                "occasion": st.session_state["results_occasion"],
            })
            engine.save("outfits", saved)
            st.session_state["flash"] = "Outfit saved."
            st.rerun()

with tab_saved:
    if not saved:
        st.info("Nothing saved yet. Save an outfit from the Outfit ideas tab.")
    for n, outfit in enumerate(saved):
        pieces = [by_id[i] for i in outfit["ids"] if i in by_id]
        st.subheader(f"{outfit['occasion'].capitalize()} outfit, score {outfit['score']}/100")
        cols = st.columns(4)
        for col, piece in zip(cols, pieces):
            with col:
                show_item(piece)
        if len(pieces) < len(outfit["ids"]):
            st.caption("Some pieces were removed from your wardrobe.")
        if st.button("Delete outfit", key=f"del_{n}"):
            engine.save("outfits", saved[:n] + saved[n + 1:])
            st.rerun()
        st.divider()
