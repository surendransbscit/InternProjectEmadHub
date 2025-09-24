from rest_framework.response import Response

def paginate_queryset(queryset, request, serializer_class):

    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    total_records = queryset.count()
    total_pages = (total_records + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    queryset = queryset[start:end]

    # Serialize
    serializer = serializer_class(queryset, many=True)

    return Response({
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "results": serializer.data
    })

