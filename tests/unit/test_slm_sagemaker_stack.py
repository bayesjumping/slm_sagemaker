import aws_cdk as core
import aws_cdk.assertions as assertions

from slm_sagemaker.slm_sagemaker_stack import SlmSagemakerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in slm_sagemaker/slm_sagemaker_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SlmSagemakerStack(app, "slm-sagemaker")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
