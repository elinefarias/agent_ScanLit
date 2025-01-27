from crewai import Task

class TextTasks():
    def summarize_task(self, agent, text, output_file):
        return Task(
            description=f'Summarize the following text:\n\n{text}',
            expected_output='A concise summary of the provided text.',
            agent=agent,
            output_file=output_file
        )