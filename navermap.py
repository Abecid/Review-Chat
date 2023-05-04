
def get_map_search_url(query):
    return f"https://m.map.naver.com/search2/search.naver?query={query}"

def get_map_id(url):
    find_keyword = 'naver.com/'
    start_id = url.find(find_keyword) + len(find_keyword)
    start_index = url.find('/', start_id) + 1
    end_index = url.find('/', start_index)
    
    if end_index == -1:
        end_index = len(url)
    
    return url[start_index:end_index]
    
    find_keyword = 'place/'
    if url.find(find_keyword) == -1:
        find_keyword = 'restaurant/'
    start_id = url.find(find_keyword) + len(find_keyword)
    end_id = url.find("/home")
    if end_id == -1:
        end_id = len(url)
    return url[start_id:end_id]

def get_map_profile_url(id):
    return f"https://m.place.naver.com/place/{id}"

def get_map_review_url(id):
    return f"https://m.place.naver.com/place/{id}/review/"

def go_to_place_page(page, wait_selector=None):
    choice = 1
    place_selector = f"#ct > div.search_listview._content._ctList > ul > li:nth-child({choice}) > div.item_info > a.a_item.a_item_distance._linkSiteview"
    page.click(place_selector)
    if wait_selector:
        page.wait_for_selector(wait_selector)
    else:
        page.wait_for_selector('body')
    # page.wait_for_selector("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH")

def get_place_info(page):
    # Return esssential information
    info = {

    }
    page.wait_for_selector("#_title > span.Fc1rA")
    official_name = page.query_selector("#_title > span.Fc1rA").inner_text()
    info["name"] = official_name
    place_type = page.query_selector("#_title > span.DJJvD").inner_text()
    info["place_type"] = place_type
    try:
        rating = page.query_selector("#app-root > div > div > div > div.place_section.OP4V8 > div.zD5Nm > div.dAsGb > span.PXMot.LXIwF > em").inner_text()   
    except Exception as e:
        rating = ''
    
    info["rating"] = rating
    page.wait_for_selector("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F")
    other_info = page.query_selector("#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F").inner_text()
    info["other"] = other_info

    return info

def get_reviews(page, place_obj, max=50):
    reviews = []
    
    one_review_type = False
    elements = page.query_selector_all('#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li')
    more_button_selector = '#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.lfH3O > a'

    num_li_elements = len(elements)
    
    if num_li_elements == 0:
        elements = page.query_selector_all('#app-root > div > div > div > div:nth-child(7) > div > div > div.place_section_content > ul')
        num_li_elements = len(elements)
        one_review_type = True
    
    index = 1
    while index <= num_li_elements:
        review_selector = f'#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li:nth-child({index}) > div.ZZ4OK > a > span.zPfVt'
        if one_review_type:
            review_selector = f'#app-root > div > div > div > div:nth-child(7) > div > div > div.place_section_content > ul > li:nth-child({index}) > a > div.icjKM > div.QDJES > div.Ns0Qo > div'
        page.wait_for_selector(review_selector)
        review = page.query_selector(review_selector).inner_text()
        date = page.query_selector(f'#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li:nth-child({index}) > div.sb8UA > span:nth-child(1) > span:nth-child(3)').inner_text()
        author = page.query_selector(f'#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li:nth-child({index}) > div.Lia3P > a.Hazns > div.sBWyy').inner_text()
        place_id = place_obj['place_id']
        source_url = f'https://m.place.naver.com/place/{place_id}/review/visitor'
        source_url = f"{source_url}#:~:text={review[:10]}"
        review = {
            "review": review,
            "date": date,
            "author": author,
            "source_url": source_url,
            "place_id": place_id,
            "place_name": place_obj['name'],
            "type": "visitor",
            "index": index
        }
        reviews.append(review)
        index += 1
        if index > max:
            break
    return reviews