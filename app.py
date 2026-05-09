---

### Push the Change to AWS
Once you save that change, run these commands in your MINGW64 terminal:

1.  **Stage and Commit:**
    ```bash
    git add app.py
    git commit -m "Update home route message for deployment test"
    ```
2.  **Push to GitHub:**
    ```bash
    git push origin main
    ```

---

### What happens next?
Because you recently pushed `.github/workflows/ci-cd.yml` to your repository, this `git push` will automatically start the following process:



*   **Build**: GitHub Actions will create a new Docker image from your code.
*   **Push**: The image will be sent to your ECR repository (`692785897749.dkr.ecr.us-east-1.amazonaws.comYour `app.py` is well-structured for a microservice, particularly with the inclusion of pre-loading the model and robust error handling. Since Git currently sees no changes, it means the version of `app.py` you have on your disk is identical to what was already committed.

To trigger your new GitHub Actions CI/CD workflow, you need to make a visible change to the file.

### Update your `home` route
To test the deployment, change the `"status"` or add a custom message in the `home()` function. For example:
```python
@app.route("/", methods=["GET"])
def home():
    """Health-check / welcome route."""
    return jsonify(
        {
            "service": "Sentiment Analysis Service",
            "version": "1.0.0",
            "status": "up and running on AWS ECS",  # Changed this line
            "message": "Welcome Sedrick!",          # Added this line
            "endpoints": {
                "GET /": "Service info",
                "POST /predict": "Predict sentiment for submitted text",
            },
        }
    )