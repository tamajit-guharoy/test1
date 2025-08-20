from playwright.sync_api import sync_playwright
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat")
def chat(content: str):
    """Synchronous endpoint for ChatGPT interaction."""
    try:
        response = callAI(content)
        return  response
    except Exception as e:
        return {"error": str(e)}

@app.get("/test")
def test():
    """Simple test endpoint to verify the server is working."""
    return {"message": "Server is running", "status": "ok"}


def callAI(content):

    with sync_playwright() as p:
        # user_data_dir = r"C:\Users\guhar\AppData\Local\Google\Chrome\User Data\Profile 2"

        # context = p.chromium.launch_persistent_context(
        #     user_data_dir=user_data_dir,
        #     channel="chrome",   # or "chrome-beta" if you want beta channel
        #     headless=False
        # )

        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]    # existing window/profile

        # Get all pages from the context
        pages = context.pages
        # Get the active page (last one if multiple are open)
        page = pages[-1] if pages else None
        # page = context.new_page()

        # page.goto("https://chatgpt.com/")
        # Wait for the input field and type "1+1"
        input_field = page.wait_for_selector('[data-placeholder="Ask anything"]', timeout=15000)
        response_elements_before = page.query_selector_all('.markdown.prose')
        count = len(response_elements_before) if response_elements_before else 0
        print(f"Number of responses before: {count}")
        print(f"Question: {content}")
        input_field.fill(content)
        # Press Enter key
        input_field.press("Enter")
        
        # # Wait for the response - look for the latest message in the thread
        # response_selector = page.wait_for_selector('.markdown.prose', timeout=30000)
        # Wait for all responses to load
        page.wait_for_timeout(5000)  # Give time for response to complete
        

        # Get all response elements
        response_elements = page.query_selector_all('.markdown.prose')

        # Wait for the new response to appear (index count+1)
        while True:
            response_elements = page.query_selector_all('.markdown.prose')
            if len(response_elements) > count:
                break
            page.wait_for_timeout(1000)  # Check every second
            
        # Get the new response element
        new_response = response_elements[count]
        response_text = new_response.inner_text()
        # Get the last (most recent) response
        # response_selector = response_elements[-1] if response_elements else None
        # if not response_selector:
        #     raise Exception("No response found")
        # response_text = response_selector.inner_text()

            
        if not response_text:
            raise Exception("Response text was empty after multiple retries")
        print("\nChatGPT Response:")
        print(response_text)
        # print("Entered '1+1' in ChatGPT input field")
        # input("Press Enter to close...")
        context.close()
        
        return response_text

if __name__ == "__main__":
    PORT = 8000
    HOST = "0.0.0.0"

    print(f"Starting FastAPI server on http://{HOST}:{PORT}")
    print(f"API Documentation: http://{HOST}:{PORT}/docs")

    # Configure uvicorn to handle synchronous operations better
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # Disable reload to avoid issues with sync operations
        log_level="info",
        loop="asyncio",  # Explicitly set the event loop
        access_log=True
    )



playwright==1.40.0

# Testing with Playwright
pytest==7.4.3
pytest-playwright==0.4.2 

# FastAPI Framework
fastapi==0.104.1
uvicorn==0.24.0
