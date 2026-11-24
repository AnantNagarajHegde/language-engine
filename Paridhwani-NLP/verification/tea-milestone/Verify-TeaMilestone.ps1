param([string]$Python='C:\Users\amogh\AppData\Local\Python\pythoncore-3.14-64\python.exe',[string]$EditorRoot='C:\Program Files\Unity\Hub\Editor\6000.6.7f1\Editor')
$ErrorActionPreference='Stop'
$nlpRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$workspaceRoot=Split-Path (Split-Path $nlpRoot -Parent) -Parent
$projectRoot=Join-Path $workspaceRoot 'game\My project (1)'
$runtimeRoot=Join-Path $projectRoot 'Assets\_Paridhwani\Scripts\Runtime'
$results=Join-Path $PSScriptRoot 'results'
$build=Join-Path $results 'Build'
New-Item -ItemType Directory -Path $build -Force | Out-Null
& $Python -I -B (Join-Path $PSScriptRoot 'generate.py') | Tee-Object -FilePath (Join-Path $results 'python-generation.txt')
if($LASTEXITCODE -ne 0){throw 'Real evaluator fixture generation failed'}
$dotnet=Join-Path $EditorRoot 'Data\NetCoreRuntime\dotnet.exe'
$csc=(Get-ChildItem (Join-Path $EditorRoot 'Data\DotNetSdk') -Filter csc.dll -Recurse | Select-Object -First 1).FullName
$cached=Get-ChildItem (Join-Path $projectRoot 'Library\Bee\artifacts') -Filter Assembly-CSharp.rsp -Recurse | Select-Object -First 1
if(!$cached){throw 'Cached compiler references unavailable; no Unity launch/import is attempted.'}
$compileArgs=Get-Content $cached.FullName | Where-Object {$_ -match '^-r:'}
$sources=@((Join-Path $nlpRoot 'integration\AssessmentConsumer.cs'),(Join-Path $nlpRoot 'integration\tea-milestone\TeaAssessmentSeam.cs'),(Join-Path $runtimeRoot 'TeaConversation.cs'),(Join-Path $runtimeRoot 'TeaProgress.cs'),(Join-Path $PSScriptRoot 'Support.cs'),(Join-Path $PSScriptRoot 'Checks.cs'))
$compileArgs+=@('-nologo','-target:exe','-main:TeaMilestoneChecks',('-out:"'+(Join-Path $build 'TeaMilestone.dll')+'"'))
$compileArgs+=$sources | ForEach-Object {'"'+$_+'"'}
$rsp=Join-Path $build 'Milestone.rsp';$compileArgs | Set-Content -LiteralPath $rsp -Encoding utf8
Push-Location $projectRoot
try {& $dotnet $csc "@$rsp" | Tee-Object -FilePath (Join-Path $results 'compile.txt');if($LASTEXITCODE -ne 0){throw 'Tea milestone compilation failed'}} finally {Pop-Location}
'{"runtimeOptions":{"tfm":"net8.0","framework":{"name":"Microsoft.NETCore.App","version":"8.0.21"}}}' | Set-Content -LiteralPath (Join-Path $build 'TeaMilestone.runtimeconfig.json')
foreach($name in @('UnityEngine.CoreModule.dll','UnityEngine.JSONSerializeModule.dll','UnityEngine.ScriptingModule.dll')){Copy-Item -LiteralPath (Join-Path $EditorRoot ('Data\Managed\UnityEngine\'+$name)) -Destination $build -Force}
& $dotnet (Join-Path $build 'TeaMilestone.dll') $results | Tee-Object -FilePath (Join-Path $results 'checks.txt')
if($LASTEXITCODE -ne 0){throw 'Tea milestone checks failed'}
& $Python -I -B (Join-Path $PSScriptRoot 'source_checks.py') | Tee-Object -FilePath (Join-Path $results 'source-checks.txt')
if($LASTEXITCODE -ne 0){throw 'Source guard checks failed; inspect source-checks.json'}
