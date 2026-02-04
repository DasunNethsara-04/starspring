"""Minimal test to debug path parameters"""

from starspring import StarSpringApplication, Controller, GetMapping

@Controller("/test")
class TestController:
    @GetMapping("/{id}")
    def get_item(self, id: int):
        print(f"get_item called with id={id}, type={type(id)}")
        return {"id": id, "message": "Success"}

app_instance = StarSpringApplication(debug=True)
app_instance.scan_components("__main__")

if __name__ == "__main__":
    print("Starting test server...")
    print("Try: curl http://localhost:8000/test/123")
    app_instance.run(port=8000)
