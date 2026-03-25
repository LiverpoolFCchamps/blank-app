import streamlit as st
import requests

# ── Page config ─────────────────────────────────────────────────────────────── 
st.set_page_config( 
    page_title="Моята библиотека",
    page_icon="📚",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .genre-badge {
        display: inline-block;
        background: #e6f1fb;
        color: #185fa5;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 500;
    }
    hr { border: none; border-top: 1px solid #eee; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "my_books"       not in st.session_state: st.session_state.my_books = {}
if "ratings"        not in st.session_state: st.session_state.ratings = {}
if "page"           not in st.session_state: st.session_state.page = "library"
if "selected_key"   not in st.session_state: st.session_state.selected_key = None
if "search_results" not in st.session_state: st.session_state.search_results = []
if "search_query"   not in st.session_state: st.session_state.search_query = ""
if "search_page"    not in st.session_state: st.session_state.search_page = 0
if "search_total"   not in st.session_state: st.session_state.search_total = 0

RESULTS_PER_PAGE = 12

# ── Open Library helpers ──────────────────────────────────────────────────────
def cover_url(cover_id, size="M"):
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"
    return None

def search_books(query, page=0):
    if not query.strip():
        return [], 0
    params = {
        "q": query,
        "fields": "key,title,author_name,first_publish_year,subject,cover_i,number_of_pages_median,isbn",
        "limit": RESULTS_PER_PAGE,
        "offset": page * RESULTS_PER_PAGE,
    }
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params=params,
            timeout=10,
            headers={"User-Agent": "MyLibraryApp/1.0 (streamlit-demo)"},
        )
        data = r.json()
        return data.get("docs", []), data.get("numFound", 0)
    except Exception:
        return [], 0

def fetch_work_details(work_key):
    try:
        r = requests.get(
            f"https://openlibrary.org{work_key}.json",
            timeout=8,
            headers={"User-Agent": "MyLibraryApp/1.0 (streamlit-demo)"},
        )
        return r.json()
    except Exception:
        return {}

def ol_doc_to_book(doc):
    cover_id = doc.get("cover_i")
    authors  = doc.get("author_name", [])
    subjects = doc.get("subject", [])
    return {
        "key":    doc.get("key", ""),
        "title":  doc.get("title", "Без заглавие"),
        "author": ", ".join(authors) if authors else "Неизвестен",
        "year":   doc.get("first_publish_year", ""),
        "genre":  ", ".join(subjects[:2]) if subjects else "",
        "cover":  cover_url(cover_id, "M"),
        "cover_l":cover_url(cover_id, "L"),
        "pages":  doc.get("number_of_pages_median", ""),
        "isbn":   (doc.get("isbn") or [None])[0],
        "price":  0.0,
    }

def avg_rating(key):
    lst = st.session_state.ratings.get(key, [])
    return sum(lst) / len(lst) if lst else 0.0

def stars_str(r, total=5):
    r = round(r)
    return "★" * r + "☆" * (total - r)

# ── Header ────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    st.markdown("# 📚 Моята библиотека")
with h2:
    n = len(st.session_state.my_books)
    st.markdown(
        f"<p style='text-align:right;color:#888;margin-top:1.5rem'>{n} запазени</p>",
        unsafe_allow_html=True,
    )
st.markdown("<hr>", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
nb1, nb2, nb3, _ = st.columns([1.5, 1.5, 1.5, 5.5])
with nb1:
    if st.button("📖 Библиотека", use_container_width=True,
                 type="primary" if st.session_state.page == "library" else "secondary"):
        st.session_state.page = "library"
        st.session_state.selected_key = None
        st.rerun()
with nb2:
    if st.button("🔍 Търси книги", use_container_width=True,
                 type="primary" if st.session_state.page == "search" else "secondary"):
        st.session_state.page = "search"
        st.session_state.selected_key = None
        st.rerun()
with nb3:
    if st.button("➕ Добави ръчно", use_container_width=True,
                 type="primary" if st.session_state.page == "add" else "secondary"):
        st.session_state.page = "add"
        st.session_state.selected_key = None
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DETAIL PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "detail" and st.session_state.selected_key:
    key  = st.session_state.selected_key
    book = st.session_state.my_books.get(key)

    if not book:
        st.warning("Книгата не е намерена.")
        st.session_state.page = "library"
        st.rerun()

    if st.button("← Назад към библиотеката"):
        st.session_state.page = "library"
        st.session_state.selected_key = None
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    img_col, info_col = st.columns([1, 3])
    with img_col:
        cover = book.get("cover_l") or book.get("cover")
        if cover:
            st.image(cover, width=180)
        else:
            st.markdown(
                "<div style='width:180px;height:240px;background:#f0f0ee;border-radius:10px;"
                "display:flex;align-items:center;justify-content:center;font-size:48px'>📕</div>",
                unsafe_allow_html=True,
            )

    with info_col:
        st.markdown(f"## {book['title']}")
        st.markdown(f"*от **{book['author']}***")

        m1, m2, m3 = st.columns(3)
        with m1:
            if book.get("year"): st.metric("Година", book["year"])
        with m2:
            if book.get("pages"): st.metric("Страници", book["pages"])
        with m3:
            st.metric("Цена", f"{book.get('price', 0):.2f} лв.")

        if book.get("genre"):
            st.markdown(f"<span class='genre-badge'>{book['genre'][:60]}</span>", unsafe_allow_html=True)

        r_list = st.session_state.ratings.get(key, [])
        avg = avg_rating(key)
        if r_list:
            st.markdown(
                f"<span style='color:#c97e1a;font-size:20px'>{stars_str(avg)}</span> "
                f"<span style='color:#888;font-size:13px'>{avg:.1f} ({len(r_list)} оценки)</span>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("Все още няма оценки")

        if book.get("isbn"):
            st.caption(f"ISBN: {book['isbn']}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Description from Open Library
    if book.get("key") and str(book["key"]).startswith("/works/"):
        with st.spinner("Зареждане на описание..."):
            details = fetch_work_details(book["key"])
        desc = details.get("description", "")
        if isinstance(desc, dict):
            desc = desc.get("value", "")
        if desc:
            st.markdown("### За книгата")
            st.markdown(
                f"<p style='color:#555;line-height:1.7'>{desc[:1500]}"
                f"{'...' if len(desc) > 1500 else ''}</p>",
                unsafe_allow_html=True,
            )
            st.markdown("<hr>", unsafe_allow_html=True)

    # Rate
    st.markdown("### ⭐ Оцени книгата")
    rating_val = st.feedback("stars", key=f"fb_{key}")
    if st.button("Запази оценката", key="save_r"):
        if rating_val is not None:
            st.session_state.ratings.setdefault(key, []).append(rating_val + 1)
            labels = ["", "Слаба", "Задоволителна", "Добра", "Много добра", "Отлична"]
            st.success(f"Оценихте с {rating_val+1}/5 — {labels[rating_val+1]}!")
            st.rerun()
        else:
            st.warning("Моля, изберете оценка.")

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🗑️ Премахни от библиотеката", type="secondary"):
        st.session_state.my_books.pop(key, None)
        st.session_state.ratings.pop(key, None)
        st.session_state.page = "library"
        st.session_state.selected_key = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "search":
    st.subheader("🔍 Търси в Open Library — над 20 млн. книги")

    with st.form("search_form"):
        qc, bc = st.columns([5, 1])
        with qc:
            query = st.text_input(
                "Търсене", value=st.session_state.search_query,
                placeholder="Заглавие, автор, тема...",
                label_visibility="collapsed",
            )
        with bc:
            submitted = st.form_submit_button("Търси", use_container_width=True, type="primary")

    if submitted and query.strip():
        st.session_state.search_query = query
        st.session_state.search_page  = 0
        with st.spinner("Търсене в Open Library..."):
            results, total = search_books(query, 0)
        st.session_state.search_results = results
        st.session_state.search_total   = total

    results = st.session_state.search_results
    total   = st.session_state.search_total

    if results:
        st.caption(f"Намерени: {total:,} книги · страница {st.session_state.search_page + 1}")

        # Pagination
        p = st.session_state.search_page
        pa, _, pb = st.columns([1, 6, 1])
        with pa:
            if p > 0 and st.button("← Предишна"):
                st.session_state.search_page -= 1
                with st.spinner("Зареждане..."):
                    res, tot = search_books(st.session_state.search_query, st.session_state.search_page)
                st.session_state.search_results = res
                st.session_state.search_total   = tot
                st.rerun()
        with pb:
            if st.button("Следваща →"):
                st.session_state.search_page += 1
                with st.spinner("Зареждане..."):
                    res, tot = search_books(st.session_state.search_query, st.session_state.search_page)
                st.session_state.search_results = res
                st.session_state.search_total   = tot
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(3)

        for i, doc in enumerate(results):
            book = ol_doc_to_book(doc)
            col  = cols[i % 3]
            with col:
                with st.container(border=True):
                    if book["cover"]:
                        st.image(book["cover"], use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height:160px;background:#f0f0ee;border-radius:8px;"
                            "display:flex;align-items:center;justify-content:center;font-size:36px'>📕</div>",
                            unsafe_allow_html=True,
                        )

                    title_short = book["title"][:50] + ("..." if len(book["title"]) > 50 else "")
                    st.markdown(f"**{title_short}**")
                    st.caption(
                        f"{book['author'][:40]}"
                        f"{'  ·  ' + str(book['year']) if book['year'] else ''}"
                    )

                    if book["genre"]:
                        st.markdown(f"<span class='genre-badge'>{book['genre'][:35]}</span>",
                                    unsafe_allow_html=True)

                    already = book["key"] in st.session_state.my_books

                    if already:
                        st.success("✓ В библиотеката")
                    else:
                        # Use expander for price input so layout doesn't jump
                        with st.expander("+ Добави в библиотеката"):
                            price = st.number_input(
                                "Цена (лв.)", min_value=0.0, step=0.50,
                                format="%.2f", key=f"price_{book['key']}_{i}",
                            )
                            if st.button("✅ Добави", key=f"confirm_{book['key']}_{i}",
                                         use_container_width=True, type="primary"):
                                book["price"] = price
                                st.session_state.my_books[book["key"]] = book
                                st.rerun()

    elif st.session_state.search_query:
        st.info("Няма намерени резултати. Опитайте с различна дума.")
    else:
        st.markdown("""
**Примерни търсения:**
- Заглавие: `War and Peace`, `Под игото`, `Harry Potter`
- Автор: `Dostoevsky`, `Agatha Christie`, `Иван Вазов`
- Тема: `science fiction`, `history`, `philosophy`
        """)


# ══════════════════════════════════════════════════════════════════════════════
# ADD MANUAL PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "add":
    st.subheader("➕ Добави книга ръчно")
    with st.form("manual_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            title  = st.text_input("Заглавие *")
            author = st.text_input("Автор *")
            genre  = st.text_input("Жанр")
        with c2:
            price = st.number_input("Цена (лв.)", min_value=0.0, step=0.50, format="%.2f")
            year  = st.text_input("Година")
            cover = st.text_input("URL на корицата")

        if cover:
            st.image(cover, width=100)

        if st.form_submit_button("✅ Добави", use_container_width=True, type="primary"):
            if not title or not author:
                st.error("Моля, попълнете заглавие и автор.")
            else:
                import time, random
                key = f"manual_{int(time.time()*1000)}_{random.randint(0, 9999)}"
                st.session_state.my_books[key] = {
                    "key": key, "title": title, "author": author,
                    "genre": genre, "price": price, "year": year,
                    "cover": cover, "cover_l": cover, "pages": "", "isbn": "",
                }
                st.success(f"„{title}" беше добавена!")
                st.session_state.page = "library"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LIBRARY PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:
    if not st.session_state.my_books:
        st.info(
            "Библиотеката е празна.  \n"
            "Отидете на **🔍 Търси книги** и добавете книги от Open Library!"
        )
    else:
        f1, f2 = st.columns([3, 1])
        with f1:
            search = st.text_input(
                "Филтрирай", placeholder="Заглавие или автор...",
                label_visibility="collapsed",
            )
        with f2:
            sort = st.selectbox(
                "Сортирай", ["По заглавие", "По оценка", "По цена"],
                label_visibility="collapsed",
            )

        books = list(st.session_state.my_books.values())

        if search:
            books = [b for b in books
                     if search.lower() in b["title"].lower()
                     or search.lower() in b["author"].lower()]

        if sort == "По оценка":
            books.sort(key=lambda b: avg_rating(b["key"]), reverse=True)
        elif sort == "По цена":
            books.sort(key=lambda b: b.get("price", 0))
        else:
            books.sort(key=lambda b: b["title"].lower())

        if not books:
            st.info("Няма книги, отговарящи на критериите.")
        else:
            cols = st.columns(3)
            for i, book in enumerate(books):
                col = cols[i % 3]
                avg = avg_rating(book["key"])
                with col:
                    with st.container(border=True):
                        if book.get("cover"):
                            st.image(book["cover"], use_container_width=True)
                        else:
                            st.markdown(
                                "<div style='height:160px;background:#f0f0ee;border-radius:8px;"
                                "display:flex;align-items:center;justify-content:center;font-size:36px'>📕</div>",
                                unsafe_allow_html=True,
                            )

                        title_short = book["title"][:48] + ("..." if len(book["title"]) > 48 else "")
                        st.markdown(f"**{title_short}**")
                        st.caption(
                            f"{book['author'][:40]}"
                            f"{'  ·  ' + str(book['year']) if book.get('year') else ''}"
                        )

                        ra, rb = st.columns([2, 1])
                        with ra:
                            if book.get("genre"):
                                st.markdown(
                                    f"<span class='genre-badge'>{book['genre'][:30]}</span>",
                                    unsafe_allow_html=True,
                                )
                        with rb:
                            st.markdown(
                                f"<div style='text-align:right;font-weight:700'>"
                                f"{book.get('price', 0):.2f} лв.</div>",
                                unsafe_allow_html=True,
                            )

                        r_list = st.session_state.ratings.get(book["key"], [])
                        if r_list:
                            st.markdown(
                                f"<span style='color:#c97e1a'>{stars_str(avg)}</span>"
                                f" <span style='font-size:12px;color:#888'>{avg:.1f}</span>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.caption("Без оценка")

                        if st.button("Виж повече", key=f"view_{book['key']}", use_container_width=True):
                            st.session_state.selected_key = book["key"]
                            st.session_state.page = "detail"
                            st.rerun()

