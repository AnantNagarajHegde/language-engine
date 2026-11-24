param([string]$EditorRoot='C:\Program Files\Unity\Hub\Editor\6000.6.7f1\Editor')
$ErrorActionPreference='Stop'
$nlpRoot=Split-Path $PSScriptRoot -Parent
$workspaceRoot=Split-Path (Split-Path $nlpRoot -Parent) -Parent
$projectRoot=Join-Path $workspaceRoot 'game\My project (1)'
$outputRoot=Join-Path $PSScriptRoot 'results\Consumer'
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
$dotnet=Join-Path $EditorRoot 'Data\NetCoreRuntime\dotnet.exe'
$csc=(Get-ChildItem (Join-Path $EditorRoot 'Data\DotNetSdk') -Recurse -Filter csc.dll | Select-Object -First 1).FullName
$cached=Get-ChildItem (Join-Path $projectRoot 'Library\Bee\artifacts') -Recurse -Filter Assembly-CSharp.rsp | Select-Object -First 1
if(!$cached){throw 'Cached Unity compiler references unavailable; no import or installation is attempted.'}
# Read cached references only. Compile this standalone sample, never game sources.
$compileArgs=Get-Content $cached.FullName | Where-Object {$_ -match '^-r:'}
$compileArgs+=@('-nologo','-target:exe',('-out:"'+(Join-Path $outputRoot 'AssessmentConsumer.dll')+'"'),('"'+(Join-Path $nlpRoot 'integration\AssessmentConsumer.cs')+'"'))
$rsp=Join-Path $outputRoot 'Consumer.rsp'
$compileArgs | Set-Content -LiteralPath $rsp -Encoding utf8
'{"runtimeOptions":{"tfm":"net8.0","framework":{"name":"Microsoft.NETCore.App","version":"8.0.21"}}}' | Set-Content -LiteralPath (Join-Path $outputRoot 'AssessmentConsumer.runtimeconfig.json')
Push-Location $projectRoot
try { & $dotnet $csc "@$rsp" | Tee-Object -FilePath (Join-Path $PSScriptRoot 'results\consumer-compile.txt');if($LASTEXITCODE -ne 0){throw 'Consumer compilation failed'} } finally {Pop-Location}
& $dotnet (Join-Path $outputRoot 'AssessmentConsumer.dll') (Join-Path $nlpRoot 'docs\fixtures') | Tee-Object -FilePath (Join-Path $PSScriptRoot 'results\consumer-check.txt')
if($LASTEXITCODE -ne 0){throw 'Consumer checks failed'}
