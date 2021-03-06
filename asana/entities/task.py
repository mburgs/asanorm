# -*- coding: utf-8 -*-

from entity import Entity
import project

class Task(Entity):
	_matchon = 'task'

	_filter_keys = [
		'project', 'assignee', 'workspace', 'completed_since', 'modified_since'
	]

	_fields = [
		'assignee','created_by','created_at','completed','completed_at',
		'followers','modified_at','name','notes','projects','parent',
		'workspace'
	]

	_children = {
		'tags': None
	}

	filter_sections = True

	@classmethod
	def _filter_result_item(cls, entity, query):
		if cls.filter_sections and cls._is_section(entity):
			return False

		return super(Task, cls)._filter_result_item(entity, query)

	@classmethod
	def _is_section(cls, ent):
		"""Checks whether a dict from the API is a section Task

		:param ent: The dict to check
		"""
		return ent['name'] and cls._is_section_name(ent['name'])

	@staticmethod
	def _is_section_name(name):
		return name and name[-1] == ':'

	def is_section(self):
		return self._is_section_name(self.name)

	def add_project(self, projectOrId):
		"""Adds this task to a project

		:param projectOrId Either the project object or a project ID
		"""
		return self._edit_project('addProject', projectOrId)

	def remove_project(self, projectOrId):
		"""Removes this task from a project

		:param projectOrId Either the project object or a project ID
		"""
		return self._edit_project('removeProject', projectOrId)

	def _edit_project(self, operation, projectOrId, data={}):
		pId = projectOrId.id if isinstance(projectOrId, project.Project) else projectOrId

		data['project'] = pId

		return self._get_api().post(
			'/'.join([self._get_item_url(), operation]),
			data=data
		)

	def add_to_section(self, section):
		"""Moves this task to a section

		If this task and the section share one or more projects the first one
		found is used. If they don't the first project in the section is used

		:param section The section to move to
		"""

		sharedProjects = set(self.projects) & set(section.projects)

		if len(sharedProjects):
			pId = sharedProjects.pop()
		else:
			pId = section.projects[0]
		
		return self._edit_project(
			'addProject',
			pId,
			{'insert_after': section.id}
		)
