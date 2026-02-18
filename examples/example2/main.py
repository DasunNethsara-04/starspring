from starspring import StarSpringApplication, TemplateEngine
from starspring.template import set_template_engine

app: StarSpringApplication = StarSpringApplication(
    title="Testing Web Application with HTML Templates",
)

# create an engine for the templates
engine = TemplateEngine(template_dir="templates")
set_template_engine(engine)

# add static files
app.add_static_files("/static", "static")

if __name__ == "__main__":
    app.run()
