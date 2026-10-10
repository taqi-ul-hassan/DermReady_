import torch
from torch import nn
from src.model import CaseGradabilityModel


def test_case_aggregation_matches_mean_and_is_order_invariant():
    model=CaseGradabilityModel.__new__(CaseGradabilityModel);nn.Module.__init__(model)
    model.backbone=nn.Identity();model.classifier=nn.Identity()
    images=torch.tensor([[1.,3.],[3.,5.],[8.,10.]])
    indices=torch.tensor([0,0,1])
    output=model(images,indices,2)
    assert torch.equal(output,torch.tensor([[2.,4.],[8.,10.]]))
    permutation=torch.tensor([2,0,1])
    assert torch.equal(output,model(images[permutation],indices[permutation],2))


def test_actual_mobilenet_case_head_dimensions():
    torch.set_num_threads(2);torch.backends.nnpack.set_flags(False)
    model=CaseGradabilityModel(pretrained=False).eval()
    with torch.inference_mode():
        output=model(torch.zeros(3,3,224,224),torch.tensor([0,0,1]),2)
    assert output.shape==(2,2) and torch.isfinite(output).all()
