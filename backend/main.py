from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scrapers.lazada import scrape_lazada, onboard_lazada
from scrapers.carousell import scrape_carousell, onboard_carousell
from models.dto import ScrapeDTO, OnboardDTO, UsernameDTO
from ai_insights import generate_product_insights
from database import get_db, DBUserProduct, DBUserActivity, DBUser, DBScrapeProduct, DBScrapeResult
from sqlalchemy.orm import Session

import json
import sys
import asyncio

if sys.platform == "win32":
     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/onboard")
def onboard(request: OnboardDTO, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == request.username).first()
    if not user:
        user = DBUser(username=request.username)
        db.add(user)
        db.flush()  # Flush to get the user.id
    
    carousell_results = []
    lazada_results = []
    shopee_results = []
    
    if request.lazada_url:
        lazada_results = onboard_lazada(str(request.lazada_url))
        # Store Lazada products
        for result in lazada_results:
            product = DBUserProduct(
                user_id=user.id,
                title=result['title'],
                price=result['price'],
                image=result['image'],
                link=result['link'],
                site="Lazada"
            )
            db.add(product)
        # Record activity
        activity = DBUserActivity(
            user_id=user.id,
            activity=f'Onboarded Lazada products'
        )
        db.add(activity)

    if request.carousell_url:
        carousell_results = onboard_carousell(str(request.carousell_url))
        
        # Store Carousell products
        for result in carousell_results:
            product = DBUserProduct(
                user_id=user.id,
                title=result['title'],
                price=result['price'],
                image=result['image'],
                link=result['link'],
                site="Carousell"
            )
            db.add(product)
            db.flush()

        # Record activity
        activity = DBUserActivity(
            user_id=user.id,
            activity=f'Onboarded Carousell products'
        )
        db.add(activity)

    # Commit all changes to database
    db.commit()
    return {
        "shopee": shopee_results,
        "lazada": lazada_results,
        "carousell": carousell_results
    }

@app.post("/scrape")
def scrape(scrape_request: ScrapeDTO, db: Session = Depends(get_db)):
    # Get user
    user = db.query(DBUser).filter(DBUser.username == scrape_request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Record scraping activity
    activity = DBUserActivity(
        user_id=user.id,
        activity=f'Scraped products for: {scrape_request.product}'
    )
    db.add(activity)
    db.commit()

    # this scrapes for lazada, default is 1 page to scrape (avoid bot detection)
    lazada_results = scrape_lazada(scrape_request.product)
    carousell_results = scrape_carousell(scrape_request.product)
    
    insights_data = {
        "lazada_average_price": lazada_results.average_price,
        "carousell_average_price": carousell_results.average_price,
        "lazada_top_listings": lazada_results.top_listings,
        "carousell_top_listings": carousell_results.top_listings
    }
    
    insights = generate_product_insights({
        "product_name": scrape_request.product,
        "insights_data": insights_data
    })

    # Create scrape result record
    scrape_result = DBScrapeResult(
        user_id=user.id,
        product_query=scrape_request.product,
        lazada_average_price=lazada_results.average_price,
        carousell_average_price=carousell_results.average_price,
        insights=json.dumps(insights)  # Convert insights to JSON string
    )
    db.add(scrape_result)
    db.flush() 

        # Save Lazada products
    for product in lazada_results.scraped_data:
        db_product = DBScrapeProduct(
            scrape_result_id=scrape_result.id,
            title=product.title,
            price=product.price,
            discount=product.discount if hasattr(product, 'discount') else None,
            image=product.image,
            link=product.link,
            site="Lazada",
            page_ranking=product.page_ranking if hasattr(product, 'page_ranking') else None
        )
        db.add(db_product)
    
    # Save Carousell products
    for product in carousell_results.scraped_data:
        db_product = DBScrapeProduct(
            scrape_result_id=scrape_result.id,
            title=product.title,
            price=product.price,
            discount=product.discount if hasattr(product, 'discount') else None,
            image=product.image,
            link=product.link,
            site="Carousell",
            page_ranking=product.page_ranking if hasattr(product, 'page_ranking') else None
        )
        db.add(db_product)
    
    db.commit()

    return {"lazada_results": lazada_results, "carousell_results": carousell_results, "insights": insights}

@app.post("/insights")
def get_insights(request: Request):
    # Get the scraped data from the request body
    data = request.json()

    # Generate AI insights using the provided scraped data
    insights = generate_product_insights({
        "product_name": data['product_name'],
        "insights_data": data['insights_data']
    })
    print(insights)
    
    return {
        "insights": insights
    }

@app.post("/dashboard")
def dashboard(dto: UsernameDTO, db: Session = Depends(get_db)):
    # Get user
    user = db.query(DBUser).filter(DBUser.username == dto.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's products using relationship
    user_products = user.products
    
    # Get user's recent activities using relationship
    user_activities = (
        db.query(DBUserActivity)
        .filter(DBUserActivity.user_id == user.id)
        .order_by(DBUserActivity.timestamp.desc())
        .limit(10)  # Get last 10 activities
        .all()
    )

    products = [{
        "title": product.title,
        "image": product.image,
        "site": product.site,
        "price": product.price,
        "link": product.link,         
        "created_at": product.created_at.strftime("%d/%m/%Y"),
    } for product in user_products]
    
    # Format activities
    activities = [{
        "activity": activity.activity,
        "date": activity.timestamp.strftime("%d/%m/%Y"),
    } for activity in user_activities]
    
    dashboard = {
        "products": products,
        "activities": activities
    }
    
    return dashboard

@app.post("/history")
def history(dto: UsernameDTO, db: Session = Depends(get_db)):
    # Get user
    user = db.query(DBUser).filter(DBUser.username == dto.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's scrape history
    scrape_results = (
        db.query(DBScrapeResult)
        .filter(DBScrapeResult.user_id == user.id)
        .order_by(DBScrapeResult.timestamp.desc())
        .all()
    )
    
    # Format response
    history_items = []
    
    for result in scrape_results:
        # Get related products
        products = db.query(DBScrapeProduct).filter(
            DBScrapeProduct.scrape_result_id == result.id
        ).all()
        
        lazada_products = [
            {
                "title": p.title,
                "price": p.price,
                "discount": p.discount,
                "image": p.image,
                "link": p.link,
                "page_ranking": p.page_ranking
            }
            for p in products if p.site == "Lazada"
        ]
        
        carousell_products = [
            {
                "title": p.title,
                "price": p.price,
                "discount": p.discount,
                "image": p.image,
                "link": p.link,
                "page_ranking": p.page_ranking
            }
            for p in products if p.site == "Carousell"
        ]
        
        history_items.append({
            "product_query": result.product_query,
            "timestamp": result.timestamp.strftime("%d/%m/%Y %H:%M"),
            "lazada_average_price": result.lazada_average_price,
            "carousell_average_price": result.carousell_average_price,
            "insights": json.loads(result.insights) if result.insights else None,
            "lazada_products": lazada_products,
            "carousell_products": carousell_products
        })
    
    return {
        "history": history_items
    }