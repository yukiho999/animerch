$url = 'https://animerch-backend.onrender.com/api/proxy/image?url=https://wx3.sinaimg.cn/mw2000/008IwfB2gy1iczekggc5hj33342bcqv6.jpg'
$resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
Write-Host "Status:" $resp.StatusCode
Write-Host "Size:" $resp.RawContentLength
