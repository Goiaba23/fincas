$scenePath = "C:\Users\alerrandro\AppData\Roaming\obs-studio\basic\scenes\Sem_nome.json"
$overlayDir = "C:\Users\alerrandro\Music\Nova pasta (2)\obs-overlays"
$backupPath = "C:\Users\alerrandro\AppData\Roaming\obs-studio\basic\scenes\Sem_nome.json.bak2"

Copy-Item $scenePath $backupPath -Force
Write-Output "Backup criado."

$json = Get-Content $scenePath -Raw -Encoding UTF8 | ConvertFrom-Json
$existingSources = $json.sources

function New-Guid { return [guid]::NewGuid().ToString() }

function New-BrowserSource($name, $uuid, $file, $w, $h) {
  return [PSCustomObject]@{
    prev_ver = 536936449
    name = $name
    uuid = $uuid
    id = "browser_source"
    versioned_id = "browser_source"
    settings = @{
      url = ""; document = ""; is_local_file = $true
      local_file = $file; width = $w; height = $h
      css = "body { background-color: rgba(0,0,0,0); margin: 0px auto; overflow: hidden; }"
      fps = 30; fps_custom = $false; shutdown = $true
      restart_when_active = $true; reroute_audio = $false; webpage_control_level = 1
    }
    mixers = 0; sync = 0; flags = 0; volume = 1.0; balance = 0.5
    enabled = $true; muted = $false
    "push-to-mute" = $false; "push-to-mute-delay" = 0
    "push-to-talk" = $false; "push-to-talk-delay" = 0
    hotkeys = @{}; deinterlace_mode = 0; deinterlace_field_order = 0
    monitoring_type = 0; private_settings = @{}
  }
}

function New-SceneItem($name, $srcUuid, $id, $x, $y, $w, $h, $sx, $sy) {
  return [PSCustomObject]@{
    name = $name; source_uuid = $srcUuid; visible = $true; locked = $false
    rot = 0.0; scale_ref = @{ x = 1360.0; y = 768.0 }; align = 5
    bounds_type = 0; bounds_align = 0; bounds_crop = $false
    crop_left = 0; crop_top = 0; crop_right = 0; crop_bottom = 0
    id = $id; group_item_backup = $false
    pos = @{ x = $x; y = $y }; pos_rel = @{ x = 0.0; y = 0.0 }
    scale = @{ x = $sx; y = $sy }; scale_rel = @{ x = $sx; y = $sy }
    bounds = @{ x = 0.0; y = 0.0 }; bounds_rel = @{ x = 0.0; y = 0.0 }
    scale_filter = "disable"; blend_method = "default"; blend_type = "normal"
    show_transition = @{ duration = 300 }; hide_transition = @{ duration = 300 }
    private_settings = @{}
  }
}

function New-Scene($name, $uuid, $items) {
  $idCounter = $items.Length
  $hkeys = @{}
  for ($i = 1; $i -le $idCounter; $i++) {
    $hkeys["libobs.show_scene_item.$i"] = @()
    $hkeys["libobs.hide_scene_item.$i"] = @()
  }
  return [PSCustomObject]@{
    prev_ver = 536936449; name = $name; uuid = $uuid
    id = "scene"; versioned_id = "scene"
    settings = @{ id_counter = $idCounter; custom_size = $false; items = $items }
    mixers = 0; sync = 0; flags = 0; volume = 1.0; balance = 0.5
    enabled = $true; muted = $false
    "push-to-mute" = $false; "push-to-mute-delay" = 0
    "push-to-talk" = $false; "push-to-talk-delay" = 0
    hotkeys = $hkeys; deinterlace_mode = 0; deinterlace_field_order = 0
    monitoring_type = 0; canvas_uuid = "6c69626f-6273-4c00-9d88-c5136d61696e"
    private_settings = @{}
  }
}

$cameraUuid = "db675438-5cee-4441-a833-1b048df78962"
$monitorUuid = "203b6131-5fca-456b-a75f-12406304a764"
$src = @(
  (New-BrowserSource "Overlay Iniciando" (New-Guid) "$overlayDir\starting-soon.html" 1920 1080)
  (New-BrowserSource "Overlay BRB" (New-Guid) "$overlayDir\brb.html" 1920 1080)
  (New-BrowserSource "Overlay Finalizando" (New-Guid) "$overlayDir\ending.html" 1920 1080)
  (New-BrowserSource "Moldura Webcam" (New-Guid) "$overlayDir\webcam-frame.html" 420 320)
  (New-BrowserSource "Barra Jogo" (New-Guid) "$overlayDir\gameplay-bar.html" 1920 60)
  (New-BrowserSource "Caixa Alertas" (New-Guid) "$overlayDir\alert-box.html" 600 200)
  (New-BrowserSource "Chat Sobreposto" (New-Guid) "$overlayDir\chat-box.html" 420 600)
  (New-BrowserSource "Overlay Conversa" (New-Guid) "$overlayDir\just-chatting.html" 1920 1080)
)

$existingSources += $src

$existingSources += (New-Scene "Iniciando" (New-Guid) @(
  (New-SceneItem "Overlay Iniciando" $src[0].uuid 1 0 0 0 0 1 1)
))

$existingSources += (New-Scene "Jogando" (New-Guid) @(
  (New-SceneItem "Captura de monitor" $monitorUuid 1 0 0 0 0 1 1),
  (New-SceneItem "camera" $cameraUuid 2 1040 40 0 0 0.8125 0.8125),
  (New-SceneItem "Moldura Webcam" $src[3].uuid 3 1036 36 0 0 1 1),
  (New-SceneItem "Barra Jogo" $src[4].uuid 4 0 714 0 0 1 1),
  (New-SceneItem "Caixa Alertas" $src[5].uuid 5 660 380 0 0 1 1),
  (New-SceneItem "Chat Sobreposto" $src[6].uuid 6 1480 200 0 0 1 1)
))

$existingSources += (New-Scene "BRB" (New-Guid) @(
  (New-SceneItem "Overlay BRB" $src[1].uuid 1 0 0 0 0 1 1)
))

$existingSources += (New-Scene "Conversa" (New-Guid) @(
  (New-SceneItem "Overlay Conversa" $src[7].uuid 1 0 0 0 0 1 1),
  (New-SceneItem "camera" $cameraUuid 2 578 265 0 0 0.8125 0.8125),
  (New-SceneItem "Caixa Alertas" $src[5].uuid 3 660 100 0 0 1 1)
))

$existingSources += (New-Scene "Finalizando" (New-Guid) @(
  (New-SceneItem "Overlay Finalizando" $src[2].uuid 1 0 0 0 0 1 1)
))

$json.sources = $existingSources
$json.scene_order = @(
  @{ name = "Iniciando" }
  @{ name = "Jogando" }
  @{ name = "BRB" }
  @{ name = "Conversa" }
  @{ name = "Finalizando" }
)
$json.current_scene = "Iniciando"
$json.current_program_scene = "Iniciando"

$json | ConvertTo-Json -Depth 10 | Set-Content $scenePath -Encoding UTF8

Write-Output "OK - OBS configurado com 5 cenas e 8 overlays."
Write-Output "Abra o OBS e veja as novas cenas."
