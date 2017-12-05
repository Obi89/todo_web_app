#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")


class Message(ndb.Model):
    name = ndb.StringProperty()
    message = ndb.TextProperty()
    check = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)


class TodoList(BaseHandler):
    def get(self):
        task = Message.query(Message.deleted == False).fetch()

        params = {"task": task}

        return self.render_template("todolist.html", params=params)

    def post(self):
        name = self.request.get("name")
        check = self.request.get("check")
        message = self.request.get("message")

        msg_object = Message(name=name, check=check, message=message.replace("<script>", ""))
        msg_object.put()
        return self.redirect_to("todo-site")


class TaskEditHandler(BaseHandler):
    def get(self, task_id):
        task = Message.get_by_id(int(task_id))

        params = {"task": task}

        return self.render_template("task_edit.html", params=params)

    def post(self, task_id):
        tasks = Message.get_by_id(int(task_id))

        name = self.request.get("name")
        text = self.request.get("message")
        status = self.request.get("check")

        tasks.message = text
        tasks.name = name
        tasks.check = status
        tasks.put()

        return self.redirect_to("todo-site")


class TaskDeleteHandler(BaseHandler):
    def get(self, task_id):
        task = Message.get_by_id(int(task_id))

        params = {"task": task}

        return self.render_template("tasks_delete.html", params=params)

    def post(self, task_id):
        tasks = Message.get_by_id(int(task_id))

        tasks.deleted = True
        tasks.put()

        return self.redirect_to("todo-site")


app = webapp2.WSGIApplication([
        webapp2.Route('/', MainHandler),
        webapp2.Route('/todolist', TodoList, name="todo-site"),
        webapp2.Route('/task/<task_id:\d+>/edit', TaskEditHandler, name="task-edit"),
        webapp2.Route('/task/<task_id:\d+>/delete', TaskDeleteHandler, name="tasks-delete"),
], debug=True)
