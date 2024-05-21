from django.http import StreamingHttpResponse

def stream_response(response):
  return StreamingHttpResponse(
    response.streaming_content,
    content_type=response.headers.get('content-type'),
    status=response.status_code,
    reason=response.reason_phrase
  )