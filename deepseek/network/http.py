import requests


def make_request(
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
) -> requests.Response:
    return requests.request(
        method,
        url,
        params=params,
        data=data,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        hooks=hooks,
        stream=stream,
        verify=verify,
        cert=cert,
        json=json,
    )

def check_response(response: requests.Response):
    response.raise_for_status()

