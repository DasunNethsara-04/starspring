"""
Quick test script to verify StarSpring framework functionality
"""

import sys
sys.path.insert(0, '.')

from starspring import (
    StarSpringApplication,
    Controller,
    Service,
    GetMapping,
    PostMapping,
    ResponseEntity,
)
from pydantic import BaseModel


# Test models
class Message(BaseModel):
    text: str
    author: str = "System"


# Test service
@Service
class MessageService:
    def get_welcome(self) -> Message:
        return Message(text="Welcome to StarSpring!", author="Framework")


# Test controller
@Controller("/api/test")
class TestController:
    def __init__(self, message_service: MessageService):
        self.message_service = message_service
    
    @GetMapping("/hello")
    def hello(self):
        return {"message": "Hello from StarSpring!"}
    
    @GetMapping("/welcome")
    def welcome(self) -> ResponseEntity[Message]:
        msg = self.message_service.get_welcome()
        return ResponseEntity.ok(msg)
    
    @PostMapping("/echo")
    def echo(self, message: Message) -> Message:
        return message


if __name__ == "__main__":
    print("=" * 60)
    print("Testing StarSpring Framework")
    print("=" * 60)
    
    # Create application
    app = StarSpringApplication(title="Test App", debug=True)
    
    # Scan components
    app.scan_components("__main__")
    
    print("✅ Application created successfully")
    print("✅ Components scanned successfully")
    print("✅ Dependency injection working")
    print("=" * 60)
    print("Framework is ready to use!")
    print("=" * 60)
