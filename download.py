with open('score.svg', 'wb') as handle:
    response = requests.get(pic_url, stream=True)

    if not response.ok:
        print(response)

    for block in response.iter_content():
        if not block:
            break

        handle.write(block)