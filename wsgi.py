import os
from app import create_app

# Create the application
app = create_app()

# For Vercel deployment
def handler(request):
    return app(request.environ, request.start_response)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)