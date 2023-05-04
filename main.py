import os
from dotenv import load_dotenv
import pandas as pd

import mongodb
import crawl as cr, navermap
import openai_api as state
from openai.embeddings_utils import get_embedding, cosine_similarity

load_dotenv()

USE_DATABASE = False

 # Search for name in database / naver map
    # Return selected name and link, Check if selected one is correct
# Crawl reviews, save in database / translate
# Start chat
# Get user query, retrieve relevant reviews from database
    # Also return source (url, full text, author, date etc.)
# synthesize reviews and use GPT-3.5 to generate a response
    # Cite sources

def chatWithReviews(chat_history, reviews):
    pass

def search_reviews(df, query_embedding, n=5):
    df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
    res = df.sort_values('similarities', ascending=False).head(n)
    return res

def main():
    crawling = True
    db = mongodb.DB('ReviewChat')
    tourism_collection = db.get_collection('tourism')
    reviews_collection = db.get_collection('reviews')
    queries_collection = db.get_collection('queries')
    item_1 = {
        "item_name" : "Blender",
        "item_price" : 100,
        "item_quantity" : 10
    }
    if USE_DATABASE:
        collection.insert_one(item_1)
        data = collection.find_one({'item_name' : 'Blender'}, {'_id': 1})
        print(data)

    crawl = cr.Crawler()
    page = crawl.get_page()
    while True:
        place = input("Enter place:\n")

        # Go to naver map search result page
        url = navermap.get_map_search_url(place)
        print(url)
        crawl.go_to_page(url)
        name_selector = '#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin.vKA6F > div > div > div.O8qbU.tQY7D > div > a > span.LDgIH'
        navermap.go_to_place_page(page, name_selector)

        # Get information
        place_page_url = page.url
        place_id = navermap.get_map_id(place_page_url)
        print('id', place_id)
        place_info = navermap.get_place_info(page)
        print(place_info)
        rating = place_info['rating']
        if len(rating) > 0:
            rating = float(rating)
        # Save place info
        place_obj = {
            'place_id': place_id,
            'name': place_info['name'],
            'type': place_info['place_type'],
            'rating': rating,
            'other': place_info['other'],
            'url': place_page_url
        }
        
        if USE_DATABASE:
            found_place = tourism_collection.find_one({'place_id': place_id}, {'_id': 1})
            if(found_place):
                # update existing data
                tourism_collection.update_one({'_id': found_place['_id']}, {'$set': place_obj})
                print('Updated place info')
            else:
                # insert new data
                tourism_collection.insert_one(place_obj)
                print('Saved place info')

        # If place exists, get reviews from database

        # Get reviews
        review_url = navermap.get_map_review_url(place_id)
        review1_selector = '#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li:nth-child(1) > div.ZZ4OK > a > span.zPfVt'
        name_selector = '#_title > span.Fc1rA'
        crawl.go_to_page(review_url, name_selector)
        reviews = navermap.get_reviews(page, place_obj, 20)
        for i in range(len(reviews)):
            review = reviews[i]
            review_text = review['review']
            embedding = state.embedding(review_text)
            review['embedding'] = embedding
            reviews[i] = review
        # Save reviews (Make review, author, place_id unique)
        if USE_DATABASE:
            reviews_collection.insert_many(reviews)
        print('Saved reviews', len(reviews))

        # Translate

        # Get blog reviews

        chat_history = []
        chat_agent = state.customChatGPT()
        system = ''
        while True:
            # Start chat
            query = input("Enter query:\n")
            query_embedding = state.embedding(query)
            query_obj = {
                'query': query,
                'embedding': query_embedding
            }

            # Get relevant reviews
            reviews_df = pd.DataFrame(reviews)
            fetched_reviews = search_reviews(reviews_df, query_embedding)
            fetched_reviews_list = fetched_reviews['review'].tolist()
            # fetched_reviews_indices = fetched_reviews.index.tolist()

            # add index number to each review

            fetched_reviews_string = '\n'.join(fetched_reviews_list)

            # Change the instruction so the response refers to the source
            instruction = f"Based on the following information, answer the following question:\n-----\n{place_info['other']}\n{fetched_reviews_string}\n-----\nQ: {query}\nA:"
            chat_history_string = '\n'.join(chat_history)
            system_description = "You are a helpful assistant. You must answer the user's question in the same language the user is asking in."
            response = state.chatGPT(f"Previous conversations: {chat_history_string}\n\n{instruction}", system_description)
            # response = chat_agent.chat(instruction)
            chat_history.append(f"{query}\n{response}")
            query_obj['response'] = response
            
            if USE_DATABASE:
                queries_collection.insert_one(query_obj)
            print(response)



if __name__ == "__main__":
    main()