$scenePath = "$env:APPDATA\obs-studio\basic\scenes\Sem_nome.json"
$overlayDir = "C:\Users\alerrandro\Music\Nova pasta (2)\obs-overlays"
$backupPath = "$env:APPDATA\obs-studio\basic\scenes\Sem_nome.json.backup"

Copy-Item $scenePath $backupPath -Force
Write-Output "Backup criado: Sem_nome.json.backup"

$json = Get-Content $scenePath -Raw | ConvertFrom-Json

$existingSources = $json.sources
$existingSceneOrder = $json.scene_order

$newUuids = @{
  "starting-soon-source" = [guid]::NewGuid().ToString()
  "brb-source"           = [guid]::NewGuid().ToString()
  "ending-source"        = [guid]::NewGuid().ToString()
  "webcam-frame-source"  = [guid]::NewGuid().ToString()
  "gameplay-bar-source"  = [guid]::NewGuid().ToString()
  "alert-box-source"     = [guid]::NewGuid().ToString()
  "chat-box-source"      = [guid]::NewGuid().ToString()
  "just-chatting-source" = [guid]::NewGuid().ToString()
  "scene-starting"       = [guid]::NewGuid().ToString()
  "scene-jogando"        = [guid]::NewGuid().ToString()
  "scene-brb"            = [guid]::NewGuid().ToString()
  "scene-conversa"       = [guid]::NewGuid().ToString()
  "scene-finalizando"    = [guid]::NewGuid().ToString()
}

function New-BrowserSource($name, $uuid, $file, $width, $height) {
  $css = "body { background-color: rgba(0,0,0,0); margin: 0px auto; overflow: hidden; }"
  return [PSCustomObject]@{
    prev_ver = 536936449
    name = $name
    uuid = $uuid
    id = "browser_source"
    versioned_id = "browser_source"
    settings = @{
      url = ""
      document = ""
      is_local_file = $true
      local_file = $file
      width = $width
      height = $height
      css = $css
      fps = 30
      fps_custom = $false
      shutdown = $true
      restart_when_active = $true
      reroute_audio = $false
      webpage_control_level = 1
    }
    mixers = 0
    sync = 0
    flags = 0
    volume = 1.0
    balance = 0.5
    enabled = $true
    muted = $false
    "push-to-mute" = $false
    "push-to-mute-delay" = 0
    "push-to-talk" = $false
    "push-to-talk-delay" = 0
    hotkeys = @{}
    deinterlace_mode = 0
    deinterlace_field_order = 0
    monitoring_type = 0
    private_settings = @{}
  }
}

function New-SceneSource($name, $sourceUuid, $idCounter, $x, $y, $w=$null, $h=$null, $scaleX=1.0, $scaleY=1.0) {
  $item = [PSCustomObject]@{
    name = $name
    source_uuid = $sourceUuid
    visible = $true
    locked = $false
    rot = 0.0
    scale_ref = @{ x = 1360.0; y = 768.0 }
    align = 5
    bounds_type = 0
    bounds_align = 0
    bounds_crop = $false
    crop_left = 0
    crop_top = 0
    crop_right = 0
    crop_bottom = 0
    id = $idCounter
    group_item_backup = $false
    pos = @{ x = $x; y = $y }
    pos_rel = @{ x = 0.0; y = 0.0 }
    scale = @{ x = $scaleX; y = $scaleY }
    scale_rel = @{ x = $scaleX; y = $scaleY }
    bounds = @{ x = 0.0; y = 0.0 }
    bounds_rel = @{ x = 0.0; y = 0.0 }
    scale_filter = "disable"
    blend_method = "default"
    blend_type = "normal"
    show_transition = @{ duration = 300 }
    hide_transition = @{ duration = 300 }
    private_settings = @{}
  }
  if ($w -and $h) {
    $item.bounds_type = 2
    $item.bounds = @{ x = $w; y = $h }
  }
  return $item
}

function New-Scene($name, $uuid, $sources) {
  $idCounter = 0
  $items = @()
  $hotkeys = @{}
  foreach ($s in $sources) {
    $idCounter++
    $items += $s
    $hotkeys["libobs.show_scene_item.$idCounter"] = @()
    $hotkeys["libobs.hide_scene_item.$idCounter"] = @()
  }
  return [PSCustomObject]@{
    prev_ver = 536936449
    name = $name
    uuid = $uuid
    id = "scene"
    versioned_id = "scene"
    settings = @{
      id_counter = $idCounter
      custom_size = $false
      items = $items
    }
    mixers = 0
    sync = 0
    flags = 0
    volume = 1.0
    balance = 0.5
    enabled = $true
    muted = $false
    "push-to-mute" = $false
    "push-to-mute-delay" = 0
    "push-to-talk" = $false
    "push-to-talk-delay" = 0
    hotkeys = $hotkeys
    deinterlace_mode = 0
    deinterlace_field_order = 0
    monitoring_type = 0
    canvas_uuid = "6c69626f-6273-4c00-9d88-c5136d61696e"
    private_settings = @{}
  }
}

Write-Output "Criando fontes Browser..."
$browserSources = @(
  (New-BrowserSource "Iniciando Overlay" $newUuids["starting-soon-source"] "$overlayDir\starting-soon.html" 1920 1080)
  (New-BrowserSource "BRB Overlay" $newUuids["brb-source"] "$overlayDir\brb.html" 1920 1080)
  (New-BrowserSource "Finalizando Overlay" $newUuids["ending-source"] "$overlayDir\ending.html" 1920 1080)
  (New-BrowserSource "Webcam Frame" $newUuids["webcam-frame-source"] "$overlayDir\webcam-frame.html" 420 320)
  (New-BrowserSource "Gameplay Bar" $newUuids["gameplay-bar-source"] "$overlayDir\gameplay-bar.html" 1920 60)
  (New-BrowserSource "Alert Box" $newUuids["alert-box-source"] "$overlayDir\alert-box.html" 600 200)
  (New-BrowserSource "Chat Box" $newUuids["chat-box-source"] "$overlayDir\chat-box.html" 420 600)
  (New-BrowserSource "Just Chatting Overlay" $newUuids["just-chatting-source"] "$overlayDir\just-chatting.html" 1920 1080)
)

$existingSources += $browserSources

Write-Output "Criando cenas..."

$cameraUuid = "db675438-5cee-4441-a833-1b048df78962"
$monitorUuid = "203b6131-5fca-456b-a75f-12406304a764"
$micUuid = "95cb904d-0baf-4dd9-9204-d90b7d5666b5"

$sceneStart = New-Scene "Iniciando" $newUuids["scene-starting"] @(
$sceneGame = New-Scene "Jogando" $newUuids["scene-jogando"] @(
$sceneBrb = New-Scene "BRB" $newUuids["scene-brb"] @(
$sceneChat = New-Scene "Conversa" $newUuids["scene-conversa"] @(
$sceneEnd = New-Scene "Finalizando" $newUuids["scene-finalizando"] @(
  (New-SceneSource "Finalizando Overlay" $newUuids["ending-source"] 1 0 0)
)

$existingSources += $sceneStart, $sceneGame, $sceneBrb, $sceneChat, $sceneEnd

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

Write-Output "=========================================="
Write-Output "✅ OBS configurado com sucesso!"
Write-Output "=========================================="
Write-Output "Cenas criadas:"
Write-Output "  [1] Iniciando   - Tela inicial + timer"
Write-Output "  [2] Jogando     - Game + webcam + barra + chat + alertas"
Write-Output "  [3] BRB         - Tela de pausa"
Write-Output "  [4] Conversa    - Camera + overlay just chatting"
Write-Output "  [5] Finalizando - Tela de encerramento"
Write-Output "=========================================="
Write-Output "Fontes adicionadas:"
Write-Output "  - Iniciando Overlay (1920x1080)"
Write-Output "  - BRB Overlay (1920x1080)"
Write-Output "  - Finalizando Overlay (1920x1080)"
Write-Output "  - Webcam Frame (420x320)"
Write-Output "  - Gameplay Bar (1920x60)"
Write-Output "  - Alert Box (600x200)"
Write-Output "  - Chat Box (420x600)"
Write-Output "  - Just Chatting Overlay (1920x1080)"
Write-Output "=========================================="
Write-Output "Para personalizar textos: edite os arquivos .html no bloco de notas"
Write-Output "Backup salvo: Sem_nome.json.backup"
