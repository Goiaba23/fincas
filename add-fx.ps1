$scenePath = "$env:APPDATA\obs-studio\basic\scenes\Sem_nome.json"
$overlayDir = "C:\Users\alerrandro\Music\Nova pasta (2)\obs-overlays"
$backupPath = "$env:APPDATA\obs-studio\basic\scenes\Sem_nome.json.bak3"

Copy-Item $scenePath $backupPath -Force
Write-Output "Backup criado."

$json = Get-Content $scenePath -Raw -Encoding UTF8 | ConvertFrom-Json

$fxUuid = [guid]::NewGuid().ToString()

$fxSource = [PSCustomObject]@{
  prev_ver = 536936449
  name = "FX Particulas + Glitch"
  uuid = $fxUuid
  id = "browser_source"
  versioned_id = "browser_source"
  settings = @{
    url = ""; document = ""; is_local_file = $true
    local_file = "$overlayDir\fx-particles-glitch.html"
    width = 1920; height = 1080
    css = "body { background-color: rgba(0,0,0,0); margin: 0px auto; overflow: hidden; }"
    fps = 60; fps_custom = $false; shutdown = $true
    restart_when_active = $true; reroute_audio = $false; webpage_control_level = 1
  }
  mixers = 0; sync = 0; flags = 0; volume = 1.0; balance = 0.5
  enabled = $true; muted = $false
  "push-to-mute" = $false; "push-to-mute-delay" = 0
  "push-to-talk" = $false; "push-to-talk-delay" = 0
  hotkeys = @{}; deinterlace_mode = 0; deinterlace_field_order = 0
  monitoring_type = 0; private_settings = @{}
}

$json.sources += $fxSource

# Add FX to Jogando scene (as top layer)
$jogandoScene = $json.sources | Where-Object { $_.name -eq "Jogando" -and $_.id -eq "scene" }
if ($jogandoScene) {
  $maxId = ($jogandoScene.settings.items | ForEach-Object { $_.id } | Measure-Object -Maximum).Maximum
  $newId = $maxId + 1
  $jogandoScene.settings.items += [PSCustomObject]@{
    name = "FX Particulas + Glitch"
    source_uuid = $fxUuid
    visible = $true; locked = $false; rot = 0.0
    scale_ref = @{ x = 1360.0; y = 768.0 }; align = 5
    bounds_type = 0; bounds_align = 0; bounds_crop = $false
    crop_left = 0; crop_top = 0; crop_right = 0; crop_bottom = 0
    id = $newId; group_item_backup = $false
    pos = @{ x = 0.0; y = 0.0 }; pos_rel = @{ x = 0.0; y = 0.0 }
    scale = @{ x = 1.0; y = 1.0 }; scale_rel = @{ x = 1.0; y = 1.0 }
    bounds = @{ x = 0.0; y = 0.0 }; bounds_rel = @{ x = 0.0; y = 0.0 }
    scale_filter = "disable"; blend_method = "default"; blend_type = "normal"
    show_transition = @{ duration = 300 }; hide_transition = @{ duration = 300 }
    private_settings = @{}
  }
  $jogandoScene.settings.id_counter = $newId
  Write-Output "FX adicionado a cena Jogando!"
}

# Add FX to Conversa scene too
$conversaScene = $json.sources | Where-Object { $_.name -eq "Conversa" -and $_.id -eq "scene" }
if ($conversaScene) {
  $maxId = ($conversaScene.settings.items | ForEach-Object { $_.id } | Measure-Object -Maximum).Maximum
  $newId = $maxId + 1
  $conversaScene.settings.items += [PSCustomObject]@{
    name = "FX Particulas + Glitch"
    source_uuid = $fxUuid
    visible = $true; locked = $false; rot = 0.0
    scale_ref = @{ x = 1360.0; y = 768.0 }; align = 5
    bounds_type = 0; bounds_align = 0; bounds_crop = $false
    crop_left = 0; crop_top = 0; crop_right = 0; crop_bottom = 0
    id = $newId; group_item_backup = $false
    pos = @{ x = 0.0; y = 0.0 }; pos_rel = @{ x = 0.0; y = 0.0 }
    scale = @{ x = 1.0; y = 1.0 }; scale_rel = @{ x = 1.0; y = 1.0 }
    bounds = @{ x = 0.0; y = 0.0 }; bounds_rel = @{ x = 0.0; y = 0.0 }
    scale_filter = "disable"; blend_method = "default"; blend_type = "normal"
    show_transition = @{ duration = 300 }; hide_transition = @{ duration = 300 }
    private_settings = @{}
  }
  $conversaScene.settings.id_counter = $newId
  Write-Output "FX adicionado a cena Conversa!"
}

$json | ConvertTo-Json -Depth 10 | Set-Content $scenePath -Encoding UTF8
Write-Output "OK - Efeitos de particulas e glitch adicionados!"
Write-Output "Abra o OBS e veja a nova fonte 'FX Particulas + Glitch' nas cenas Jogando e Conversa."
