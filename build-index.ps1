#requires -version 5.1
<#
.SYNOPSIS
  _INDEX/OVERVIEW 목차 생성기 (CONVENTIONS §4의 "결정적 생성"을 실제로 수행).

.DESCRIPTION
  루트의 분류 폴더(컨테이너) 안 각 프로젝트(잎)의 HANDOFF.md frontmatter(status·updated·summary·repo)를
  스캔해, 각 컨테이너의 _INDEX.md와 루트 OVERVIEW.md의 AUTO 영역을 재생성한다.

  - 컨테이너는 자동 탐색: $Containers가 비면 루트 직속 하위폴더(., _ 로 시작하는 meta 제외)를 모두 분류로 본다.
  - 생성 영역은 <!-- AUTO:START --> ~ <!-- AUTO:END --> 사이뿐.
  - 마커 밖 텍스트(H1, 큐레이션 `> 주의:` 메모 등)는 그대로 보존한다.
  - 출력은 UTF-8 BOM + LF (PS5.1 한글 깨짐 방지).
  - 멱등: 같은 입력이면 두 번 돌려도 바이트 동일.
  - PowerShell 없는 환경(mac/linux 등)에선 build-index.py가 동일 출력을 낸다 — 한쪽을 고치면 다른 쪽도 같이 고친다.

.PARAMETER Root
  dev 루트. 기본 = 이 스크립트 위치.

.PARAMETER Check
  파일을 쓰지 않고 변경 필요 여부만 보고. 변경 필요하면 exit 1 (CI/검증용).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File ./build-index.ps1   # Windows (PS 5.1 기본 탑재)
  pwsh -File ./build-index.ps1                                  # PowerShell 7 (Win/mac/linux)
  pwsh -File ./build-index.ps1 -Check                           # 변경 필요 여부만 (CI)
  python3 build-index.py                                        # PowerShell 없을 때 (동일 출력)
#>
[CmdletBinding()]
param(
  [string]$Root = $PSScriptRoot,
  [switch]$Check
)

$ErrorActionPreference = 'Stop'
# PS 5.1 + [CmdletBinding()]에선 param 기본값의 $PSScriptRoot가 바인딩 시점에 빈 문자열일 수 있어 본문에서 다시 잡는다.
if (-not $Root) { $Root = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path } }

# --- 설정 (조정 가능) ---
$Containers  = @()                          # 분류 폴더명. 비우면 자동 탐색(루트 직속 하위, ._ 제외). 특정 폴더만/순서 고정 시에만 명시.
$Labels      = @{}                          # 분류 폴더별 한 줄 설명 (선택 — 없으면 라벨 생략)
$StatusOrder = @('운영','개발','기획','보류')          # 표시 순서(0건은 생략)
$StatusAliases = @{ planning = '기획'; building = '개발'; live = '운영'; paused = '보류' }
$MetaDirs    = @('docs')                     # 루트 직속 meta 폴더(공유 자산) — 컨테이너 스캔 제외 (CONVENTIONS §1·§8)
$ProjectDocs = @('PLAN.md','HANDOFF.md','LOG.md','README.md','CLAUDE.md')
$GenNote     = '> **생성물** (CONVENTIONS §4). 직접 편집 금지 — `build-index` 재생성. 최종 생성: {0}'

$Today   = (Get-Date).ToString('yyyy-MM-dd')
$Utf8Bom = New-Object System.Text.UTF8Encoding($true)
$Warnings = New-Object System.Collections.Generic.List[string]
$START = '<!-- AUTO:START -->'
$END   = '<!-- AUTO:END -->'

function Read-Text([string]$path) {
  return ([System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)) -replace "`r`n","`n"
}
function Write-TextBom([string]$path, [string]$text) {
  $text = ($text -replace "`r`n","`n")
  [System.IO.File]::WriteAllText($path, $text, $Utf8Bom)
}

function Parse-Frontmatter([string]$handoffPath) {
  $lines = (Read-Text $handoffPath) -split "`n"
  if ($lines.Count -lt 2 -or $lines[0].Trim() -ne '---') { return $null }
  $fm = @{}
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq '---') { break }
    $m = [regex]::Match($lines[$i], '^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$')
    if ($m.Success) { $fm[$m.Groups[1].Value] = $m.Groups[2].Value.Trim() }
  }
  return $fm
}

function Get-Leaves([string]$containerPath) {
  $leaves = @()
  $dirs = @(Get-ChildItem -LiteralPath $containerPath -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notmatch '^[._]' })
  if ($dirs.Count -gt 1) {
    [Array]::Sort($dirs, [System.Comparison[object]]{ param($a, $b) [string]::CompareOrdinal($a.Name, $b.Name) })
  }
  foreach ($d in $dirs) {
    $handoff = Join-Path $d.FullName 'HANDOFF.md'
    if (Test-Path -LiteralPath $handoff) {
      $fm = Parse-Frontmatter $handoff
      if (-not $fm) { $Warnings.Add("$($d.FullName): HANDOFF frontmatter 파싱 실패 — 제외"); continue }
      $status  = if ($fm.ContainsKey('status')  -and $fm['status'])  { $fm['status'] }  else { '?' }
      if ($StatusAliases.ContainsKey($status.ToLower())) { $status = $StatusAliases[$status.ToLower()] }
      $summary = if ($fm.ContainsKey('summary')) { $fm['summary'] } else { '' }
      $repo    = if ($fm.ContainsKey('repo')     -and $fm['repo'])    { $fm['repo'] }    else { '' }
      if ($repo -match '<org>|<name>') { $Warnings.Add("$($d.FullName): HANDOFF repo가 미충전 placeholder('$repo') — 실제 repo로 바꾸거나 줄 삭제") }
      if ($StatusOrder -notcontains $status) { $Warnings.Add("$($d.FullName): HANDOFF status '$status'가 규약 값(기획·개발·운영·보류 / planning·building·live·paused) 밖 — 오타/placeholder 확인") }
      $updated = if ($fm.ContainsKey('updated') -and $fm['updated']) { $fm['updated'] } else { '' }
      if ($updated -notmatch '^\d{4}-\d{2}-\d{2}$') { $Warnings.Add("$($d.FullName): HANDOFF updated '$updated'가 YYYY-MM-DD 형식 아님(미충전 placeholder?) — 세션 종료 시 갱신") }
      $leaves += [pscustomobject]@{ Name = $d.Name; Status = $status; Summary = $summary; Repo = $repo }
    }
    else {
      $hasDoc = $false
      foreach ($doc in $ProjectDocs) { if (Test-Path -LiteralPath (Join-Path $d.FullName $doc)) { $hasDoc = $true; break } }
      $nested = Get-ChildItem -LiteralPath $d.FullName -Directory -Recurse -ErrorAction SilentlyContinue |
                Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'HANDOFF.md') } | Select-Object -First 1
      if     ($nested) { $Warnings.Add("$($d.FullName): 중첩 컨테이너로 보임(하위에 HANDOFF) — 스크립트 미지원, 확장 필요") }
      elseif ($hasDoc) { $Warnings.Add("$($d.FullName): 프로젝트 문서는 있으나 HANDOFF.md 없음 — 카탈로그 제외(HANDOFF 생성 필요)") }
      else             { $Warnings.Add("$($d.FullName): 프로젝트 문서 없음(빈/비-프로젝트) — 제외(정체 확인 필요)") }
    }
  }
  return ,$leaves
}

function Format-Count($leaves) {
  $parts = @()
  foreach ($s in $StatusOrder) {
    $c = @($leaves | Where-Object { $_.Status -eq $s }).Count
    if ($c -gt 0) { $parts += "$s $c" }
  }
  foreach ($g in ($leaves | Where-Object { $StatusOrder -notcontains $_.Status } | Group-Object Status)) {
    $parts += "$($g.Name) $($g.Count)"
  }
  return ($parts -join ' · ')
}

function Count-Or($leaves) { $c = Format-Count $leaves; if ($c) { $c } else { '아직 없음' } }

function Repo-Cell([string]$repo) { if ($repo) { return $repo } else { return '_(로컬)_' } }

function Build-Table($leaves, [string]$pathPrefix) {
  $rows = @('| 프로젝트 | 상태 | repo | 한 줄 |', '|---|---|---|---|')
  foreach ($l in $leaves) {
    $rows += "| [$($l.Name)]($pathPrefix$($l.Name)/) | $($l.Status) | $(Repo-Cell $l.Repo) | $($l.Summary) |"
  }
  return ($rows -join "`n")
}

function Splice-Auto([string]$path, [string]$fallbackTitle, [string]$autoContent) {
  $block = "$START`n$autoContent`n$END"
  if (Test-Path -LiteralPath $path) {
    $existing = Read-Text $path
    $iS = $existing.IndexOf($START); $iE = $existing.IndexOf($END)
    if ($iS -ge 0 -and $iE -gt $iS) {
      return $existing.Substring(0, $iS) + $block + $existing.Substring($iE + $END.Length)
    }
    if ($existing.Trim()) {
      $Warnings.Add("${path}: AUTO 마커 없음 — 기존 내용 보존하고 끝에 AUTO 블록 추가. 원하는 위치에 마커를 넣고 재실행.")
      return ($existing.TrimEnd() + "`n`n" + $block + "`n")
    }
  }
  return "$fallbackTitle`n`n$block`n"
}

function Commit([string]$path, [string]$newContent) {
  $old = if (Test-Path -LiteralPath $path) { Read-Text $path } else { '' }
  $new = $newContent -replace "`r`n","`n"
  if ($old -eq $new) { Write-Host "  =  $path"; return $false }
  if ($Check) { Write-Host "  ~  $path  (변경 필요)" -ForegroundColor Yellow; return $true }
  Write-TextBom $path $new
  Write-Host "  +  $path  (갱신)" -ForegroundColor Green
  return $true
}

# --- 메인 ---
Write-Host "build-index — Root: $Root  ($Today)"

# 컨테이너 자동 탐색: 명시 안 했으면 루트 직속 하위폴더(., _ 로 시작하는 meta·스크래치 제외)를 분류로 본다.
if (-not $Containers -or $Containers.Count -eq 0) {
  $found = @(Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue |
             Where-Object { $_.Name -notmatch '^[._]' } | ForEach-Object { $_.Name })
  if ($found.Count -gt 1) { [Array]::Sort($found, [System.StringComparer]::Ordinal) }
  $Containers = $found
}
$Containers = @($Containers | Where-Object { $MetaDirs -notcontains $_ })  # 루트 meta(docs 등) 제외
if (-not $Containers -or $Containers.Count -eq 0) {
  $Warnings.Add("분류 폴더가 없음 — 빈 워크스페이스로 OVERVIEW만 생성. (프로젝트는 분류 폴더 안에 _templates/ 복사로 만든다)")
}

$allLeaves = @()
$ovSections = New-Object System.Collections.Generic.List[string]
$changed = $false

foreach ($c in $Containers) {
  $cpath = Join-Path $Root $c
  if (-not (Test-Path -LiteralPath $cpath)) { $Warnings.Add("컨테이너 없음: $cpath"); continue }
  $leaves = Get-Leaves $cpath
  $allLeaves += $leaves

  $idxAuto = ($GenNote -f $Today) + "`n`n" + (Build-Table $leaves '') + "`n`n_상태: $(Count-Or $leaves)_"
  $idxContent = Splice-Auto (Join-Path $cpath '_INDEX.md') "# $c — 프로젝트 목차" $idxAuto
  if (Commit (Join-Path $cpath '_INDEX.md') $idxContent) { $changed = $true }

  $label = if ($Labels.ContainsKey($c)) { $Labels[$c] } else { '' }
  $head = "## $c ($($leaves.Count))"
  if ($label) { $head += " — $label" }
  $head += " · [목차]($c/_INDEX.md)"
  $ovSections.Add("$head`n`n" + (Build-Table $leaves "$c/"))
}

$ovAuto = ($GenNote -f $Today) + "`n`n" +
          "전체 $($allLeaves.Count)개 — **$(Count-Or $allLeaves)**. 규약: [CONVENTIONS.md](CONVENTIONS.md)`n`n" +
          ($ovSections -join "`n`n")
$ovContent = Splice-Auto (Join-Path $Root 'OVERVIEW.md') "# $(Split-Path $Root -Leaf) — 프로젝트 지도 (OVERVIEW)" $ovAuto
if (Commit (Join-Path $Root 'OVERVIEW.md') $ovContent) { $changed = $true }

# --- 경고 ---
if ($Warnings.Count -gt 0) {
  Write-Host "`n경고 ($($Warnings.Count)):" -ForegroundColor Yellow
  foreach ($w in $Warnings) { Write-Host "  ! $w" -ForegroundColor Yellow }
}
Write-Host "`n잎 $($allLeaves.Count)개 — $(Count-Or $allLeaves)"

if ($Check -and $changed) { exit 1 }
exit 0
