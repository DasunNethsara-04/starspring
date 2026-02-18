from starlette.middleware.sessions import SessionMiddleware
from starspring import StarSpringApplication, TemplateEngine
from starspring.template import set_template_engine

app = StarSpringApplication(
    title="Session Based Authentication with StarSpring",
)

app.add_middleware(SessionMiddleware, secret_key="key")

# engine for the template
engine = TemplateEngine(template_dir="templates")
set_template_engine(engine)

if __name__ == "__main__":
    app.run()