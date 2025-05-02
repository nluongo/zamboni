from unittest.mock import MagicMock, patch
import torch
from zamboni.training import Trainer

def test_train():
    mock_model = MagicMock()
    mock_model.num_classes = 1
    mock_model.return_value = torch.tensor([[0.5]])
    mock_optimizer = MagicMock()
    trainer = Trainer(mock_model, mock_optimizer)

    train_loader = [([torch.tensor([[0.1]]), None, torch.tensor([1])])]
    #trainer.train(train_loader, train_epochs=1, log_step=False)

    with patch('torch.Tensor.backward') as mock_backward:  # Mock loss.backward()
        trainer.train(train_loader, train_epochs=1, log_step=False)
        mock_backward.assert_called()  # Ensure backward is called

    mock_optimizer.zero_grad.assert_called()
    mock_optimizer.step.assert_called()

def test_calculate_loss_binary():
    mock_model = type('MockModel', (), {'num_classes': 1})()
    trainer = Trainer(mock_model, None)
    outputs = torch.tensor([[0.5], [0.7]])
    labels = torch.tensor([1, 0])
    loss = trainer.calculate_loss(outputs, labels)
    assert loss.item() > 0

def test_calculate_loss_multiclass():
    mock_model = type('MockModel', (), {'num_classes': 3})()
    trainer = Trainer(mock_model, None)
    outputs = torch.tensor([[0.2, 0.5, 0.3], [0.1, 0.8, 0.1]])
    labels = torch.tensor([1, 2])
    loss = trainer.calculate_loss(outputs, labels)
    assert loss.item() > 0