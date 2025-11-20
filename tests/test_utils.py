from app.utils import r2_upload


def test_upload_to_r2_mocked(mocker):
    mock_upload = mocker.patch(
        "app.utils.r2_upload.upload_to_r2",
        return_value="https://cdn.example.com/test.jpg",
    )

    result = r2_upload.upload_to_r2("test.jpg")

    assert result.startswith("https://")
    assert "test.jpg" in result
    mock_upload.assert_called_once_with("test.jpg")
