from dusty.data_model.canonical_model import DefaultModel


class PTAIModel(DefaultModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finding['title'] = kwargs.get('title')
        self.scan_type = 'SAST'

    def wrap_jira_comment(self, comment):
        return comment

    def jira_steps_to_reproduce(self):
        pass
