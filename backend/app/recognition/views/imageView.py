import logging
import base64
from io import BytesIO

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from PIL import Image

from recognition.serializers.catchSerializer import (
    ImageUploadSerializer,
    ImageProcessingResponseSerializer,
)
from services.recognition.catch_extractor import extract_fishes
from services.llm.exceptions import LlmUpstreamError, LlmTimeoutError, LlmInvalidResponseError

log = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_catch_from_image(request):
    """从上传的截图识别渔获。
    Response: {"image": <base64 png>, "fishes": [[freshness, name, weight, price], ...]}
    """
    serializer = ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    upload = serializer.validated_data['image']
    try:
        image = Image.open(upload).convert("RGB")
    except Exception as e:
        return Response({"detail": f"无法解析图片: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        annotated, fishes = extract_fishes(image=image)
    except LlmTimeoutError as e:
        log.warning("VLM timeout: %s", e)
        return Response(
            {"detail": "模型调用超时，请稍后重试", "code": "LLM_TIMEOUT"},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except LlmUpstreamError as e:
        log.warning("VLM upstream failure: %s", e)
        return Response(
            {"detail": "上游模型暂不可用，请稍后重试", "code": "LLM_UPSTREAM_ERROR"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except LlmInvalidResponseError as e:
        log.warning("VLM invalid response: %s", e)
        return Response(
            {"detail": "模型返回内容无法解析", "code": "LLM_INVALID_RESPONSE"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    buf = BytesIO()
    annotated.save(buf, format="PNG")
    image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    payload = {"image": image_b64, "fishes": fishes}
    resp = ImageProcessingResponseSerializer(data=payload)
    resp.is_valid(raise_exception=True)
    return Response(resp.validated_data)
