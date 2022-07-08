import aws_cdk as core
import aws_cdk.assertions as assertions

from HubStacks.first_stack import FirstStack

def test_sqs_queue_created():
    app = core.App()
    stack = FirstStack(app, "FirstStack")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
