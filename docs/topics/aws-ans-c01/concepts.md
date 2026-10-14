# 기본 개념

AWS Certified Advanced Networking – Specialty(ANS-C01)의 핵심 개념 40개를 시험 도메인별로 정리했다. 중요도 ★★★는 기출 빈도가 높은 개념이다.

!!! note "수치 표기"
    수치는 AWS 공식 문서(2026년 10월 확인)를 기준으로 했다. 공식 문서로 다시 확인하지 못한 값에는 `(확인 필요)`를 붙였다. 쿼터는 자주 바뀌므로 시험 직전에 한 번 더 확인한다.

## 목차

| 영역 | 개념 | 중요도 |
|------|------|--------|
| 설계(D1) | [AWS Direct Connect 연결](#direct-connect) | ★★★ |
| 설계(D1) | [BGP 경로 제어](#bgp-path-selection) | ★★★ |
| 설계(D1) | [Transit Gateway Connect](#tgw-connect) | ★★ |
| 설계(D1) | [VPC 피어링](#vpc-peering) | ★★ |
| 설계(D1) | [AWS Transit Gateway](#transit-gateway) | ★★★ |
| 설계(D1) | [AWS PrivateLink 엔드포인트 서비스](#privatelink) | ★★★ |
| 설계(D1) | [IP 주소 관리·고갈·중복 대응](#ip-address-management) | ★★ |
| 설계(D1) | [Route 53 퍼블릭 호스팅 영역·위임·DNSSEC](#route53-public-zone) | ★★ |
| 설계(D1) | [Route 53 라우팅 정책·헬스 체크](#route53-routing-policy) | ★★ |
| 설계(D1) | [Route 53 프라이빗 호스팅 영역](#route53-private-hosted-zone) | ★★★ |
| 설계(D1) | [Resolver 인바운드 엔드포인트](#route53-resolver-inbound) | ★★★ |
| 설계(D1) | [Resolver 아웃바운드 엔드포인트·전달 규칙](#route53-resolver-outbound) | ★★★ |
| 설계(D1) | [Application Load Balancer](#alb) | ★★★ |
| 설계(D1) | [Network Load Balancer](#nlb) | ★★★ |
| 설계(D1) | [Gateway Load Balancer](#gwlb) | ★★ |
| 설계(D1) | [Amazon CloudFront](#cloudfront) | ★★ |
| 설계(D1) | [AWS Global Accelerator](#global-accelerator) | ★★ |
| 구현(D2) | [프라이빗 VIF](#private-vif) | ★★★ |
| 구현(D2) | [퍼블릭 VIF](#public-vif) | ★★ |
| 구현(D2) | [트랜짓 VIF](#transit-vif) | ★★★ |
| 구현(D2) | [Direct Connect 게이트웨이](#dx-gateway) | ★★★ |
| 구현(D2) | [AWS Site-to-Site VPN](#site-to-site-vpn) | ★★★ |
| 구현(D2) | [TGW 라우팅 테이블·연결·전파](#tgw-route-table) | ★★★ |
| 구현(D2) | [인터페이스 VPC 엔드포인트](#interface-endpoint) | ★★★ |
| 구현(D2) | [게이트웨이 VPC 엔드포인트](#gateway-endpoint) | ★★ |
| 구현(D2) | [AWS RAM 리소스 공유](#ram-sharing) | ★★ |
| 구현(D2) | [네트워크 IaC·이벤트 기반 자동화](#network-automation) | ★ |
| 운영(D3) | [NAT 게이트웨이](#nat-gateway) | ★★★ |
| 운영(D3) | [VPC Flow Logs](#vpc-flow-logs) | ★★★ |
| 운영(D3) | [VPC Traffic Mirroring](#traffic-mirroring) | ★★ |
| 운영(D3) | [VPC Reachability Analyzer](#reachability-analyzer) | ★★ |
| 운영(D3) | [Network Manager·Route Analyzer](#tgw-network-manager) | ★★ |
| 운영(D3) | [향상된 네트워킹·MTU 최적화](#enhanced-networking) | ★ |
| 보안(D4) | [보안 그룹·네트워크 ACL](#security-group-nacl) | ★★★ |
| 보안(D4) | [AWS Network Firewall](#network-firewall) | ★★ |
| 보안(D4) | [TGW 어플라이언스 모드](#tgw-appliance-mode) | ★★ |
| 보안(D4) | [Direct Connect MACsec](#macsec) | ★★ |
| 보안(D4) | [DX 위 IPsec VPN](#vpn-over-dx) | ★★ |
| 보안(D4) | [로드 밸런서 TLS·인증서](#elb-tls) | ★★ |
| 보안(D4) | [WAF·Shield·Firewall Manager·DNS Firewall](#perimeter-protection) | ★ |

---

## 설계 (D1, 30%)

### AWS Direct Connect 연결 {#direct-connect}

**온프레미스와 AWS를 잇는 전용 물리 회선이다. 그 위에 VLAN 단위의 가상 인터페이스(VIF)를 만들고 BGP로 경로를 주고받는다.**

인터넷을 거치지 않으므로 대역폭과 지연이 일정하다. 대용량 하이브리드 트래픽, 일관된 성능, 규정 준수가 요구될 때 쓴다.

- 연결 종류: **전용 연결(Dedicated)** 은 1/10/100/400Gbps 포트이고, **호스티드 연결(Hosted)** 은 파트너가 제공하며 VIF를 1개만 만들 수 있다.
- 구축 절차: 연결 요청 → **LOA-CFA** 를 받아 DX 로케이션에서 크로스 커넥트 → VIF 생성(802.1Q VLAN 1~4094, BGP). BGP MD5 인증은 기본으로 켜져 있다.
- **LAG**: 같은 속도의 연결을 묶는다. 100G 미만은 최대 4개, 100G는 최대 2개다.
- 복원력: 최고 복원력은 **DX 로케이션 2곳 × 회선 2개씩** 이다. 비용을 낮춘 백업은 Site-to-Site VPN이다.
- 빠른 장애 감지는 **BFD** 를 고객 라우터에 설정한다(BGP 홀드 타이머보다 빠르다). 기본 간격 300ms × 배수 3 (확인 필요)
- 관련: [프라이빗 VIF](#private-vif), [퍼블릭 VIF](#public-vif), [트랜짓 VIF](#transit-vif), [DX 게이트웨이](#dx-gateway), [MACsec](#macsec)

[헷갈리는 개념 → BGP 트래픽 제어](confusions.md#bgp-traffic-steering) · [SD-WAN 하이브리드](confusions.md#sdwan-hybrid)

### BGP 경로 제어(AS_PATH·Local Pref·커뮤니티) {#bgp-path-selection}

**DX/VPN에서 어떤 경로로 트래픽을 보낼지 BGP 속성으로 정하는 방법이다. 방향(AWS→온프레미스 / 온프레미스→AWS)마다 쓰는 도구가 다르다.**

active/passive나 active/active 설계, 특정 리전·회선 우선 문제의 핵심이다.

- **AWS→온프레미스 경로 선택 순서(프라이빗·트랜짓 VIF)**: 가장 긴 프리픽스 → Local Preference 커뮤니티 → AS_PATH 길이 → MED 순이다.
- **Local Pref 커뮤니티**: `7224:7100` 낮음, `7224:7200` 중간, `7224:7300` 높음. AS_PATH보다 먼저 평가된다. 태그가 없으면 DX 로케이션과 같은 연관 리전(associated Region)을 우선한다.
- 같은 커뮤니티·같은 AS_PATH 길이면 여러 VIF에 **ECMP** 로 분산한다(active/active).
- **온프레미스→AWS 방향** 은 고객 라우터의 Local Pref로 정한다. AWS가 받는 쪽 경로를 유도하려면 **AS_PATH 프리펜드** 나 더 구체적인 프리픽스를 쓴다.
- 같은 프리픽스를 DX와 VPN이 모두 광고하면 AWS는 DX 경로를 우선한다.
- 퍼블릭 VIF에서 사설 ASN을 쓰면 AWS가 7224로 바꾸므로 프리펜드가 외부에 효과가 없다.

[헷갈리는 개념 → BGP 트래픽 제어](confusions.md#bgp-traffic-steering)

### Transit Gateway Connect {#tgw-connect}

**기존 VPC 어태치먼트나 DX 어태치먼트를 전송 경로로 삼아, GRE 터널 + BGP로 SD-WAN 가상 어플라이언스를 TGW에 붙이는 어태치먼트다.**

SD-WAN을 AWS로 확장할 때 IPsec 오버헤드 없이 높은 대역폭이 필요하면 쓴다.

- 전송(transport) 어태치먼트(VPC 또는 DX)가 먼저 있어야 한다. 인터넷 위 IPsec이 아니다.
- **Connect 피어(GRE 터널)당 최대 5Gbps**, 어태치먼트당 피어 최대 4개(합계 최대 20Gbps)다.
- 여러 Connect 피어에 걸쳐 ECMP로 수평 확장한다. 같은 피어 안의 BGP 세션 사이에서는 ECMP를 하지 않는다.
- TGW에 Connect용 CIDR 블록(TGW당 최대 5개)을 지정해 GRE 끝점 주소로 쓴다.
- 관련: [Transit Gateway](#transit-gateway), [Site-to-Site VPN](#site-to-site-vpn)

[헷갈리는 개념 → SD-WAN 하이브리드](confusions.md#sdwan-hybrid)

### VPC 피어링 {#vpc-peering}

**두 VPC를 1:1로 잇는 비전이적 연결이다. 리전과 계정을 넘을 수 있다.**

소수 VPC를 가장 싸고 단순하게 연결할 때 쓴다(시간당 요금이 없다).

- **비전이적**: A-B, B-C가 피어링이어도 A-C는 통하지 않는다.
- **엣지 간 라우팅 불가**: 피어 VPC의 IGW, NAT 게이트웨이, VPN, DX, 게이트웨이 엔드포인트를 빌려 쓸 수 없다.
- CIDR이 겹치면 피어링을 만들 수 없다.
- 양쪽 라우팅 테이블에 경로를 직접 추가해야 하고, 다른 VPC의 SG를 참조할 수 있다(같은 리전).
- 리전 간 피어링의 MTU는 8500이다.
- VPC 수가 많아지면 메시 관리가 어려워져 [Transit Gateway](#transit-gateway)로 옮긴다.

[헷갈리는 개념 → VPC 간 연결](confusions.md#vpc-interconnect)

### AWS Transit Gateway {#transit-gateway}

**리전 단위의 관리형 허브-스포크 라우터다. VPC, VPN, DX 게이트웨이, Connect, 피어링 어태치먼트를 한 곳에 모은다.**

수십~수천 개 VPC와 온프레미스를 전이적으로 연결할 때 쓴다. 피어링 메시와 EC2 기반 트랜짓 VPC를 대체한다.

- 쿼터: TGW당 어태치먼트 5,000개, 라우팅 테이블 20개, 전체 경로 10,000개.
- **대역폭**: VPC 어태치먼트당 AZ별 방향마다 최대 100Gbps. **MTU 8500**(VPC·DX·Connect·피어링), VPN은 1500이다.
- **리전 간 TGW 피어링** 은 정적 경로만 쓴다(BGP 동적 전파 없음). 두 TGW 사이 피어링은 1개만 만들 수 있다.
- PMTUD는 VPC·Connect 어태치먼트 인그레스에서만 지원하고 VPN·DX·피어링에서는 지원하지 않는다.
- 다른 계정과는 [RAM](#ram-sharing)으로 공유한다. 글로벌 규모에서는 **AWS Cloud WAN**(코어 네트워크 정책, 세그먼트)으로 확장한다.
- 관련: [TGW 라우팅 테이블](#tgw-route-table), [어플라이언스 모드](#tgw-appliance-mode), [DX 게이트웨이](#dx-gateway)

[헷갈리는 개념 → VPC 간 연결](confusions.md#vpc-interconnect) · [DX 게이트웨이와 전이 라우팅](confusions.md#dx-gateway-transit)

### AWS PrivateLink 엔드포인트 서비스 {#privatelink}

**제공자가 NLB(또는 GWLB) 뒤의 서비스를 엔드포인트 서비스로 노출하고, 소비자는 자기 VPC의 인터페이스 엔드포인트로 단방향 접근하는 방식이다.**

SaaS나 공유 서비스를 다른 VPC·계정에 내보낼 때, 특히 **CIDR이 겹칠 때** 쓴다.

- 소비자→제공자 방향만 연결을 시작할 수 있다(단방향). 전체 네트워크를 열지 않는다.
- 제공자 측은 [NLB](#nlb)가 필수다(어플라이언스용은 [GWLB](#gwlb)).
- 소비자 쪽 ENI IP로 접근하므로 양쪽 VPC CIDR이 겹쳐도 된다.
- 허용 주체(allowed principals)와 연결 수락(acceptance required)으로 접근을 통제한다.
- 프라이빗 DNS 이름을 쓰려면 제공자가 도메인 소유권을 검증해야 한다.
- 관련: [인터페이스 엔드포인트](#interface-endpoint)

[헷갈리는 개념 → VPC 엔드포인트 종류](confusions.md#vpc-endpoint-type) · [VPC 간 연결](confusions.md#vpc-interconnect) · [NAT와 IP 고갈](confusions.md#nat-ip-exhaustion)

### IP 주소 관리·고갈·중복 대응 {#ip-address-management}

**VPC CIDR 설계와 운영 중 IP 고갈·CIDR 중복을 해결하는 도구 모음이다(보조 CIDR, VPC IPAM, 프라이빗 NAT 게이트웨이).**

조직 전체에서 겹치지 않는 주소를 배정하거나, 이미 겹친 네트워크를 연결해야 할 때 쓴다.

- **보조 CIDR**: 기존 VPC에 CIDR을 추가해 서브넷을 늘린다(예: 100.64.0.0/10 대역을 워크로드용으로).
- **VPC IPAM**: 풀 계층(최상위→리전→계정)과 할당 규칙으로 CIDR을 자동 배정한다. 풀은 [RAM](#ram-sharing)으로 공유하고, SCP로 "IPAM 풀에서만 VPC 생성"을 강제한다.
- **프라이빗 NAT 게이트웨이**: 겹치는 대역의 워크로드를 겹치지 않는 대역 IP로 변환해 TGW·VGW 너머와 통신시킨다.
- CIDR이 겹친 채로 서비스 하나만 노출하면 되면 [PrivateLink](#privatelink)가 더 간단하다.
- 관련: [NAT 게이트웨이](#nat-gateway)

[헷갈리는 개념 → NAT와 IP 고갈](confusions.md#nat-ip-exhaustion)

### Route 53 퍼블릭 호스팅 영역·위임·DNSSEC {#route53-public-zone}

**인터넷에 공개되는 권한 DNS 영역이다. 하위 도메인 위임, 도메인 이전, TTL, DNSSEC 서명을 다룬다.**

- **하위 도메인 위임**: 하위 영역(다른 계정 가능)을 만들고, 부모 영역에 그 영역의 **NS 레코드** 를 추가한다.
- 등록 기관을 옮길 때는 먼저 TTL을 낮추고 NS를 바꾸는 순서로 다운타임을 줄인다.
- **DNSSEC**: KSK는 고객 관리 KMS 키(us-east-1의 비대칭 키, 확인 필요)로 만들고, ZSK는 Route 53이 관리한다. 신뢰 체인을 완성하려면 **부모 영역에 DS 레코드** 를 등록한다. 영역당 KSK는 최대 2개다.
- Alias 레코드는 AWS 리소스(ELB, CloudFront 등)를 가리키며 영역 꼭대기(apex)에도 쓸 수 있다.

[헷갈리는 개념 → DNS 영역 범위](confusions.md#dns-zone-scope)

### Route 53 라우팅 정책·헬스 체크 {#route53-routing-policy}

**DNS 응답을 정책(지연 시간, 가중치, 장애 조치, 지리 위치 등)과 헬스 체크로 바꿔 트래픽을 분산하는 기능이다.**

- **지연 시간**: 사용자에게 지연이 가장 낮은 리전. **가중치**: 비율 분산(블루/그린). **장애 조치**: 기본 → 보조. **지리 위치/근접성**: 사용자 위치 기반.
- 헬스 체크 결과에 따라 비정상 레코드를 응답에서 뺀다. Alias 레코드는 "대상 상태 평가"를 쓸 수 있다.
- ALB/NLB 같은 AWS 리소스는 CNAME 대신 **alias** 로 가리킨다.
- DNS 기반이라 클라이언트 캐시(TTL) 때문에 전환이 늦다. 즉시 전환이 필요하면 [Global Accelerator](#global-accelerator)를 고려한다.

[헷갈리는 개념 → 글로벌 트래픽](confusions.md#global-traffic)

### Route 53 프라이빗 호스팅 영역 {#route53-private-hosted-zone}

**연결(association)한 VPC 안에서만 응답하는 DNS 영역이다.**

사내 도메인(예: `corp.internal`)을 VPC 안에서만 해석하거나, 같은 이름의 퍼블릭 영역과 나눠 split-horizon을 만들 때 쓴다.

- VPC에 **enableDnsSupport** 와 **enableDnsHostnames** 가 모두 켜져 있어야 동작한다. 진단형 문제의 단골 원인이다.
- **다른 계정 VPC 연결**: PHZ 소유 계정에서 연결 승인(authorization)을 만들고, VPC 계정에서 연결한다(CLI/API/SDK).
- 영역당 연결할 수 있는 VPC는 300개다. 더 많으면 **Route 53 Profiles** 를 쓴다.
- **split-horizon**: 같은 이름의 퍼블릭·프라이빗 영역이 있으면 연결된 VPC 안에서는 프라이빗 영역이 응답한다.
- 온프레미스에서는 직접 보이지 않는다. [인바운드 엔드포인트](#route53-resolver-inbound)를 거쳐야 한다.
- 인터페이스 엔드포인트를 중앙 VPC에서 공유할 때 프라이빗 DNS를 끄고 서비스 이름의 PHZ를 만들어 스포크 VPC에 연결한다.

[헷갈리는 개념 → DNS 영역 범위](confusions.md#dns-zone-scope)

### Route 53 Resolver 인바운드 엔드포인트 {#route53-resolver-inbound}

**온프레미스 DNS 서버가 VPC의 Route 53 Resolver에 질의할 수 있게 VPC 안에 만드는 ENI IP 집합이다. 방향: 온프레미스 → AWS.**

온프레미스에서 PHZ 레코드나 VPC 내부 이름(인터페이스 엔드포인트 이름 등)을 해석할 때 쓴다.

- 온프레미스 DNS에 **조건부 전달자** 를 만들어 대상 도메인을 인바운드 엔드포인트 IP로 보낸다.
- 고가용성을 위해 IP를 서로 다른 AZ에 2개 이상 둔다. 엔드포인트당 IP 최대 6개(증가 가능)다.
- **IP 하나당 UDP 최대 10,000 QPS**. 제한적인 SG 규칙으로 연결 추적이 일어나면 1,500 QPS까지 떨어질 수 있다.
- SG에서 온프레미스 DNS 서버의 TCP/UDP 53을 허용해야 한다.
- DX나 VPN으로 VPC에 닿을 수 있어야 한다. EC2 기반 BIND 포워더보다 운영 부담이 적다.

[헷갈리는 개념 → Resolver 방향](confusions.md#resolver-direction) · [DNS 영역 범위](confusions.md#dns-zone-scope)

### Route 53 Resolver 아웃바운드 엔드포인트·전달 규칙 {#route53-resolver-outbound}

**VPC 안의 질의를 전달 규칙(도메인 → 대상 DNS IP)에 따라 온프레미스 DNS로 보내는 엔드포인트다. 방향: AWS → 온프레미스.**

- 구성 3요소: **아웃바운드 엔드포인트** + **전달 규칙(Forward rule)** + **규칙과 VPC 연결**.
- 규칙은 [RAM](#ram-sharing)으로 다른 계정에 공유하고, 각 계정이 자기 VPC에 연결한다. 엔드포인트는 중앙 VPC 하나에만 두면 된다.
- 하위 도메인 예외는 **시스템 규칙(System rule)** 으로 Resolver가 직접 처리하게 한다. 더 구체적인 도메인 규칙이 우선한다.
- 쿼터: 리전당 규칙 1,000개, 규칙당 대상 IP 6개, 규칙-VPC 연결 2,000개.
- 양방향 해석 문제는 인바운드와 아웃바운드를 **둘 다** 고른다.

[헷갈리는 개념 → Resolver 방향](confusions.md#resolver-direction)

### Application Load Balancer {#alb}

**HTTP/HTTPS를 처리하는 L7 로드 밸런서다. 요청 내용(경로, 호스트, 헤더)으로 대상 그룹을 고른다.**

- 경로·호스트·헤더·쿼리 기반 라우팅, 리디렉션, 고정 응답, 인증(OIDC/Cognito).
- **스티키 세션**(쿠키), **slow start**, 가중치 대상 그룹.
- 대상 유형: 인스턴스, **IP**(피어 VPC나 DX/VPN 너머 온프레미스 서버 가능), Lambda.
- 클라이언트 IP는 **X-Forwarded-For** 헤더로 전달한다(소스 IP는 ALB 노드 IP로 바뀐다).
- 고정 IP가 없다. 고정 IP가 필요하면 [Global Accelerator](#global-accelerator)를 앞에 두거나 NLB→ALB 대상 구성을 쓴다.
- 서브넷 크기 최소 /27 (확인 필요)
- 관련: [로드 밸런서 TLS](#elb-tls), [CloudFront](#cloudfront)

[헷갈리는 개념 → 로드 밸런서 종류](confusions.md#load-balancer-type)

### Network Load Balancer {#nlb}

**TCP/UDP/TLS를 처리하는 L4 로드 밸런서다. AZ마다 고정 IP를 갖고 대량 연결을 낮은 지연으로 처리한다.**

- AZ마다 고정 IP 1개. 인터넷 연결형이면 **EIP** 를 붙일 수 있어 방화벽 허용 목록에 넣기 좋다.
- **TLS 패스스루**: TCP 리스너로 받으면 암호화를 대상까지 그대로 보낸다. TLS 리스너로 종료도 할 수 있다.
- **클라이언트 IP 보존**: 인스턴스 대상은 기본으로 보존한다. IP 대상 등 보존이 안 되는 경우 **Proxy Protocol v2** 를 켠다.
- TCP 유휴 타임아웃 기본 **350초**(60~6000초로 변경 가능), TLS 리스너는 350초 고정, UDP는 120초 고정.
- 교차 영역 로드 밸런싱은 기본 꺼짐이다.
- [PrivateLink](#privatelink) 엔드포인트 서비스의 전면에 둔다.

[헷갈리는 개념 → 로드 밸런서 종류](confusions.md#load-balancer-type)

### Gateway Load Balancer {#gwlb}

**서드파티 방화벽·IDS 어플라이언스 플릿을 트래픽 경로에 투명하게 끼워 넣는 L3 로드 밸런서다.**

- 어플라이언스와는 **GENEVE** 캡슐화(UDP 6081, 확인 필요)로 원본 패킷을 그대로 주고받는다.
- 트래픽은 **GWLB 엔드포인트(GWLBE)** 를 라우팅 테이블 대상으로 지정해 보낸다(PrivateLink 기반이라 다른 VPC에서 쓸 수 있다).
- 흐름별 고정(5-tuple 등)으로 같은 흐름은 같은 어플라이언스로 간다.
- 중앙 검사 VPC를 TGW에 붙일 때는 [어플라이언스 모드](#tgw-appliance-mode)를 함께 켠다.
- 관리형 IPS로 충분하면 [Network Firewall](#network-firewall)이 운영 부담이 적다.

[헷갈리는 개념 → 로드 밸런서 종류](confusions.md#load-balancer-type) · [검사 삽입 방식](confusions.md#inspection-insertion)

### Amazon CloudFront {#cloudfront}

**엣지 로케이션에서 콘텐츠를 캐싱하는 CDN이다. HTTP/HTTPS 전용이다.**

- 정적·동적 웹 콘텐츠의 지연을 줄이고 오리진 부하를 덜 때 쓴다.
- **오리진 보호**: (1) 오리진 SG에 CloudFront 관리형 프리픽스 리스트만 허용, (2) CloudFront가 붙이는 커스텀 헤더를 ALB의 WAF 규칙으로 검사한다. S3 오리진은 OAC를 쓴다.
- **필드 레벨 암호화**: 특정 POST 필드를 엣지에서 공개 키로 암호화한다.
- Lambda@Edge / CloudFront Functions로 엣지에서 요청·응답을 바꾼다.
- 인증서는 **us-east-1** 의 ACM 인증서를 쓴다.
- 비HTTP 트래픽이나 고정 IP가 필요하면 [Global Accelerator](#global-accelerator)다.

[헷갈리는 개념 → 글로벌 트래픽](confusions.md#global-traffic)

### AWS Global Accelerator {#global-accelerator}

**고정 애니캐스트 IP로 받은 TCP/UDP 트래픽을 AWS 글로벌 백본을 통해 가장 가까운 정상 리전 엔드포인트로 보내는 서비스다. 캐싱은 하지 않는다.**

- 고정 애니캐스트 IPv4 2개를 제공한다(BYOIP 가능). 클라이언트 허용 목록 문제에 유리하다.
- 엔드포인트: ALB, NLB, EC2, EIP. 엔드포인트 그룹(리전)별 트래픽 다이얼, 엔드포인트 가중치를 둔다.
- 헬스 체크 기반으로 DNS TTL과 무관하게 **빠르게 장애 조치** 한다.
- 게임(UDP), IoT, VoIP처럼 비HTTP 성능 개선에 쓴다.
- [가속 Site-to-Site VPN](#site-to-site-vpn)도 Global Accelerator 엣지를 쓴다.

[헷갈리는 개념 → 글로벌 트래픽](confusions.md#global-traffic)

---

## 구현 (D2, 26%)

### 프라이빗 VIF {#private-vif}

**DX 위에서 VPC의 사설 IP에 접근하는 가상 인터페이스다. VGW에 직접 붙이거나 DX 게이트웨이를 거쳐 여러 리전의 VGW에 붙인다.**

- 전용 연결당 프라이빗+퍼블릭 VIF 최대 50개, 호스티드 연결은 VIF 1개.
- **온프레미스→AWS 광고 프리픽스는 BGP 세션당 기본 100개**(IPv4, IPv6 각각). 넘으면 BGP 세션이 idle(DOWN)이 된다 → **경로 요약** 이 정답. 프리픽스 제어(prefix controls)로 최대 1,000개까지 늘릴 수 있다.
- **MTU 1500 또는 9001**(점보). 점보로 바꾸면 물리 연결이 최대 30초 끊길 수 있다.
- VLAN 태그는 연결에서 고유해야 하고 생성 후 바꿀 수 없다. 고객 ASN은 VGW/DXGW ASN과 같으면 안 된다.
- **SiteLink**: DX 로케이션끼리 리전을 거치지 않고 AWS 백본으로 직접 통신한다. DXGW에 붙은 프라이빗 VIF와 트랜짓 VIF에서 지원하고, VGW에 직접 붙은 VIF와 퍼블릭 VIF는 지원하지 않는다.
- 진단 단골: VLAN 불일치, BGP 피어 IP/ASN/MD5 키 오류.

[헷갈리는 개념 → VIF 종류](confusions.md#dx-vif-type)

### 퍼블릭 VIF {#public-vif}

**DX로 AWS 퍼블릭 엔드포인트(S3, DynamoDB, 퍼블릭 API, 다른 리전 퍼블릭 IP 등)에 접근하는 가상 인터페이스다.**

- 고객이 소유한(RIR에 등록된) 퍼블릭 IP 프리픽스가 필요하다. ASN은 퍼블릭이나 사설 모두 가능하다.
- BGP 세션당 경로 1,000개(증가 불가). AWS는 모든 리전의 퍼블릭 프리픽스를 광고한다.
- **스코프 커뮤니티**(고객이 붙임): `7224:9100` 로컬 리전, `7224:9200` 대륙, `7224:9300` 전역(기본값).
- AWS가 광고하는 경로에는 `7224:8100`(같은 리전), `7224:8200`(같은 대륙) 태그와 NO_EXPORT가 붙는다.
- 전이 라우팅은 안 된다. 그 위에 IPsec VPN을 올려 암호화한다([DX 위 VPN](#vpn-over-dx)).

[헷갈리는 개념 → VIF 종류](confusions.md#dx-vif-type)

### 트랜짓 VIF {#transit-vif}

**DX 게이트웨이에 연결된 Transit Gateway로 향하는 가상 인터페이스다. 다수 VPC로 확장하는 표준 경로다.**

- 속도와 상관없이 전용·호스티드 연결 모두에서 만들 수 있다. 전용 연결당 최대 4개다.
- **MTU 1500 또는 8500**(프라이빗 VIF의 9001과 다르다).
- AWS→온프레미스 광고는 DXGW-TGW 연결의 **허용 프리픽스** 로 정해지며 TGW당 IPv4+IPv6 합계 200개다.
- 온프레미스→AWS는 BGP 세션당 기본 100개다(프라이빗 VIF와 같다).
- IPv4와 IPv6는 각각 별도 BGP 피어를 둔다(같은 주소 체계로 세션 2개는 불가).

[헷갈리는 개념 → VIF 종류](confusions.md#dx-vif-type) · [DX 게이트웨이와 전이 라우팅](confusions.md#dx-gateway-transit)

### Direct Connect 게이트웨이 {#dx-gateway}

**VIF를 여러 리전의 VGW나 TGW에 연결해 주는 글로벌 객체다. 라우터가 아니라 연결 중계자다.**

- 연결 대상: 프라이빗 VIF ↔ VGW(DXGW당 최대 20개), 트랜짓 VIF ↔ TGW(DXGW당 최대 6개). DXGW당 VIF 최대 30개.
- **전이 라우팅을 하지 않는다**: VIF↔VIF(SiteLink 제외), VGW↔VGW(VPC↔VPC) 통신 불가. 리전 간 VPC 통신은 TGW 피어링을 쓴다.
- **허용 프리픽스(allowed prefixes)** 목록이 온프레미스로 광고할 범위를 정한다. 누락하면 경로가 안 보인다.
- 다른 계정의 VGW/TGW는 **연결 제안(association proposal)** 을 보내고 DXGW 소유자가 수락한다.
- 연결된 VPC CIDR끼리 겹치면 안 된다.

[헷갈리는 개념 → DX 게이트웨이와 전이 라우팅](confusions.md#dx-gateway-transit)

### AWS Site-to-Site VPN {#site-to-site-vpn}

**VGW나 TGW에 종단하는 관리형 IPsec VPN이다. 연결 하나에 서로 다른 AZ의 터널 2개가 있다.**

빠른 구축, DX 백업, DX 위 암호화에 쓴다.

- **터널당 최대 1.25Gbps, 140,000 PPS**. 대용량(large bandwidth) 터널은 최대 5Gbps다(지원 조건 확인 필요).
- 처리량을 늘리려면 **TGW + 동적 라우팅(BGP) + ECMP** 로 여러 터널을 묶는다. 정적 라우팅이나 VGW에서는 ECMP가 안 된다.
- **MTU 1446 / MSS 1406**, 점보 프레임과 PMTUD는 지원하지 않는다.
- 경로 쿼터: CGW→VGW 동적 경로 100개, CGW→TGW 1,000개.
- **가속 VPN**: Global Accelerator 엣지로 들어온다. TGW 어태치먼트에서만 쓸 수 있다.
- 정적/동적 라우팅, IKEv2, DPD 타임아웃 동작(clear/restart/none), 인증서 기반 CGW(고정 IP가 없을 때)를 설정할 수 있다.

[헷갈리는 개념 → DX 암호화](confusions.md#dx-encryption) · [BGP 트래픽 제어](confusions.md#bgp-traffic-steering) · [SD-WAN 하이브리드](confusions.md#sdwan-hybrid)

### Transit Gateway 라우팅 테이블·연결·전파 {#tgw-route-table}

**어태치먼트를 라우팅 테이블에 연결(association)하고 경로를 전파(propagation)해 네트워크를 세그먼트로 나누는 방식이다.**

- **연결**: 어태치먼트는 라우팅 테이블 하나에만 연결된다. 그 어태치먼트에서 **들어온** 트래픽이 어느 테이블을 볼지 정한다.
- **전파**: 어태치먼트의 CIDR(또는 BGP 경로)을 테이블에 자동 등록한다. 여러 테이블에 전파할 수 있다.
- 격리 예: 운영/개발 테이블을 따로 두고 서로 전파하지 않는다. 공유 서비스 VPC는 양쪽에 전파한다.
- **검사 VPC 경유**: 스포크 테이블에는 0.0.0.0/0 → 검사 VPC 정적 경로, 검사 VPC 테이블에는 스포크 경로를 전파한다.
- **블랙홀 경로** 로 특정 대역을 차단한다. 고객 관리형 프리픽스 리스트를 참조할 수 있다.
- 관련: [Transit Gateway](#transit-gateway), [어플라이언스 모드](#tgw-appliance-mode)

### 인터페이스 VPC 엔드포인트 {#interface-endpoint}

**서브넷에 ENI를 만들어 AWS 서비스나 PrivateLink 서비스에 사설 IP로 접근하는 엔드포인트다.**

- 대부분의 AWS 서비스(SQS, KMS, SSM, STS, S3 등)를 지원한다. 시간당 + 처리량 요금이 있다.
- **ENI라서 온프레미스(DX/VPN)나 피어 VPC, TGW 너머에서도 접근할 수 있다.** 이것이 게이트웨이 엔드포인트와의 결정적 차이다.
- **프라이빗 DNS** 를 켜면 서비스 기본 이름이 엔드포인트 IP로 해석된다(enableDnsSupport/Hostnames 필요).
- 엔드포인트에 **SG** 를 붙이고(443 허용), **엔드포인트 정책** 으로 접근 가능한 리소스를 제한한다.
- **중앙 공유 패턴**: 공유 VPC에 엔드포인트를 두고 프라이빗 DNS를 끈 뒤, 서비스 이름의 PHZ를 만들어 스포크 VPC에 연결한다. 온프레미스는 [인바운드 엔드포인트](#route53-resolver-inbound)로 해석한다.

[헷갈리는 개념 → VPC 엔드포인트 종류](confusions.md#vpc-endpoint-type)

### 게이트웨이 VPC 엔드포인트 {#gateway-endpoint}

**S3와 DynamoDB 전용 무료 엔드포인트다. 라우팅 테이블에 서비스 프리픽스 리스트 경로를 추가하는 방식이다.**

- 추가 요금이 없어 같은 VPC 안의 S3 트래픽 비용 절감(NAT 처리 비용 회피)에 최적이다.
- 라우팅 테이블 기반이라 **같은 VPC 안에서만** 쓸 수 있다. 온프레미스, 피어 VPC, TGW 너머에서는 쓸 수 없다.
- ENI·SG가 없다. 엔드포인트 정책과 S3 버킷 정책(`aws:sourceVpce`)으로 접근을 통제한다.
- 같은 리전의 서비스에만 접근한다.
- 온프레미스에서 S3에 사설 접근하라는 문제는 S3 [인터페이스 엔드포인트](#interface-endpoint)가 정답이다.

[헷갈리는 개념 → VPC 엔드포인트 종류](confusions.md#vpc-endpoint-type)

### AWS RAM 리소스 공유 {#ram-sharing}

**AWS Resource Access Manager로 리소스를 다른 계정이나 조직(OU)과 공유하는 서비스다.**

- 네트워크 시험에서 공유하는 대상: **TGW**, **Resolver 규칙**, **고객 관리형 프리픽스 리스트**, **서브넷(VPC 공유)**, **IPAM 풀**, Network Firewall 정책 등.
- Organizations에서 RAM 공유를 활성화하면 조직 안 계정은 초대 수락 없이 공유된다.
- **VPC 공유**: 소유 계정이 VPC·라우팅·NAT를 관리하고, 참여 계정은 공유 서브넷에 리소스만 만든다. 네트워크 중앙 관리와 IP 절약에 유리하다.
- TGW를 공유받은 계정은 자기 VPC 어태치먼트를 만들고, TGW 소유자가 수락(자동 수락 설정 가능)한다.

### 네트워크 IaC·이벤트 기반 자동화 {#network-automation}

**CloudFormation, CDK, EventBridge, Lambda, AWS Config로 네트워크를 코드로 배포하고 변경을 감지·대응하는 방법이다.**

- **CloudFormation**: 리소스 생성 순서는 `DependsOn`(예: IGW 연결 후 경로 생성). 지원하지 않는 작업은 **커스텀 리소스 + Lambda** 로 처리한다.
- **CDK**: 값을 하드코딩하지 않고 컨텍스트·파라미터로 환경별 재사용.
- **EventBridge + Lambda**: 네트워크 이벤트(Network Manager 토폴로지·경로 변경 등)에 자동 대응.
- **AWS Config 규칙**: SG 0.0.0.0/0 허용 같은 비준수 구성을 감지하고 자동 수정(SSM Automation)한다.

---

## 운영 (D3, 20%)

### NAT 게이트웨이 {#nat-gateway}

**AZ 단위의 관리형 NAT다. 퍼블릭 NAT는 사설 서브넷의 아웃바운드 인터넷 접근을, 프라이빗 NAT는 사설망 간 주소 변환을 맡는다.**

- **유휴 타임아웃 350초**: 350초 이상 유휴인 연결은 끊기고 NAT가 RST를 돌려준다(FIN 아님). 해결은 **TCP keepalive를 350초 미만** 으로 설정한다. 지표 `IdleTimeoutCount` 로 감시한다.
- **포트 고갈**: IP 하나당 **고유 목적지별 동시 연결 최대 55,000개**. 넘으면 `ErrorPortAllocation` 이 오른다. 해결은 보조 IP 추가, NAT 게이트웨이 추가 분산, 연결 수 제한.
- **AZ 이중화**: AZ마다 NAT 게이트웨이를 두고 각 AZ 라우팅 테이블이 자기 AZ의 NAT를 가리키게 한다.
- 퍼블릭 NAT는 퍼블릭 서브넷에 두고 VPC에 IGW가 있어야 한다. 프라이빗 NAT는 EIP 없이 TGW·VGW로 보낸다.
- 지원 프로토콜: TCP, UDP, ICMP. IPsec은 NAT-T(UDP 캡슐화)로만 통과한다. TCP/ICMP IP 프래그먼트를 지원하지 않는다.
- 기본 쿼터: AZ당 NAT 게이트웨이 5개(증가 가능).

[헷갈리는 개념 → NAT와 IP 고갈](confusions.md#nat-ip-exhaustion)

### VPC Flow Logs {#vpc-flow-logs}

**ENI·서브넷·VPC 단위로 IP 흐름의 메타데이터(주소, 포트, 프로토콜, 바이트, ACCEPT/REJECT)를 기록하는 기능이다. 패킷 내용(페이로드)은 담지 않는다.**

- 대상: **CloudWatch Logs**(Logs Insights로 질의, 지표 필터·알람), **S3**(Athena로 질의), Kinesis Data Firehose.
- **사용자 지정 형식**: `pkt-srcaddr`/`pkt-dstaddr`(NAT·중간 장치 뒤의 원래 IP), `tcp-flags`, `flow-direction`, `traffic-path`, `vpc-id` 등을 추가한다.
- 형식은 생성 후 바꿀 수 없다. 새 플로 로그를 만든다.
- SG/NACL 진단: 인바운드 ACCEPT + 아웃바운드 REJECT면 상태 비저장인 **NACL** 반환 규칙 누락이다.
- 기록하지 않는 트래픽: Amazon DNS 서버 질의, 인스턴스 메타데이터(169.254.169.254), DHCP 등.

[헷갈리는 개념 → 경로 분석 도구](confusions.md#path-analysis-tools)

### VPC Traffic Mirroring {#traffic-mirroring}

**ENI의 실제 패킷(페이로드 포함)을 복제해 분석 장비로 보내는 기능이다.**

- 구성: **미러 소스(ENI)** → **미러 필터**(방향, 프로토콜, 포트, CIDR) → **미러 타깃**(ENI, NLB, GWLB 엔드포인트).
- 복제 패킷은 VXLAN으로 캡슐화되어 전달된다.
- L7 분석, IDS, 포렌식처럼 **페이로드** 가 필요할 때 쓴다(Flow Logs로는 불가).
- 여러 소스를 NLB나 GWLB 엔드포인트 타깃으로 모아 분석 플릿에 분산한다.
- Nitro 기반 인스턴스에서 지원한다.

[헷갈리는 개념 → 경로 분석 도구](confusions.md#path-analysis-tools)

### VPC Reachability Analyzer {#reachability-analyzer}

**두 리소스 사이의 연결 가능성을 실제 패킷 없이 구성(라우팅 테이블, SG, NACL, 게이트웨이 등)만으로 분석하는 도구다.**

- 도달 불가면 어느 구성 요소가 막는지(예: SG 규칙 없음, 경로 없음)를 알려 준다.
- 소스·목적지: 인스턴스, ENI, IGW, VPC 엔드포인트, TGW 어태치먼트, VPN 게이트웨이 등.
- 분석 경로를 저장해 두고 변경 후 다시 실행할 수 있다. EventBridge·Lambda와 묶어 변경 후 자동 검증에 쓴다.
- 실제 트래픽을 보려면 [Flow Logs](#vpc-flow-logs), 리전 간 TGW 경로는 [Route Analyzer](#tgw-network-manager)를 쓴다.

[헷갈리는 개념 → 경로 분석 도구](confusions.md#path-analysis-tools)

### Network Manager·Route Analyzer {#tgw-network-manager}

**여러 리전의 TGW와 온프레미스 장치를 글로벌 네트워크로 묶어 토폴로지, 경로, 이벤트를 한곳에서 보는 서비스다(AWS Network Manager).**

- 글로벌 네트워크에 TGW를 등록하고 사이트·장치·링크(SD-WAN 포함)를 표현한다.
- **Route Analyzer**: TGW 라우팅 테이블 기준으로 소스→목적지 경로를 분석한다. **TGW 피어링을 넘는 리전 간 경로** 도 분석한다.
- 토폴로지 변경, 경로 변경, 상태 이벤트를 **CloudWatch Logs / EventBridge** 로 보내 알림·자동화를 건다.
- Cloud WAN도 Network Manager에서 관리한다.

[헷갈리는 개념 → 경로 분석 도구](confusions.md#path-analysis-tools)

### 향상된 네트워킹·MTU 최적화 {#enhanced-networking}

**ENA/EFA, 배치 그룹, 점보 프레임으로 인스턴스 간 처리량과 지연을 최적화하는 방법이다.**

- **ENA**: SR-IOV 기반 향상된 네트워킹. **EFA**: HPC·ML용 OS 바이패스 통신.
- **클러스터 배치 그룹**: 한 AZ 안에 가깝게 배치해 지연을 최소화한다. 점보 프레임과 함께 권장한다.
- **MTU 정리**:

| 경로 | MTU |
|------|-----|
| VPC 안(점보) | 9001 |
| IGW, Site-to-Site VPN, TGW 없는 리전 간 | 1500 (VPN은 실효 1446) |
| 리전 간 VPC 피어링 | 8500 |
| Transit Gateway(VPC·DX·Connect·피어링) | 8500 |
| DX 프라이빗 VIF / 트랜짓 VIF | 9001 / 8500 |

- MTU를 넘는 패킷은 쪼개지거나 DF 비트가 있으면 버려진다. PMTUD가 동작하려면 ICMP(Type 3 Code 4)를 SG/NACL에서 허용해야 한다.

---

## 보안 (D4, 24%)

### 보안 그룹·네트워크 ACL {#security-group-nacl}

**SG는 ENI 단위 상태 저장 방화벽, NACL은 서브넷 단위 상태 비저장 방화벽이다.**

| 항목 | 보안 그룹(SG) | 네트워크 ACL(NACL) |
|------|--------------|-------------------|
| 적용 단위 | ENI | 서브넷 |
| 상태 | 상태 저장(응답 자동 허용) | 상태 비저장(반환 규칙 필요) |
| 규칙 | 허용만 | 허용 + 거부 |
| 평가 | 모든 규칙 | 번호 낮은 순, 첫 일치 |
| 참조 | CIDR, 프리픽스 리스트, 다른 SG | CIDR만 |

- NACL 반환 트래픽은 **임시 포트 1024-65535** 를 허용해야 한다. 누락이 진단 문제의 단골이다.
- 특정 IP **차단** 은 NACL 거부 규칙으로 한다(SG는 거부 불가).
- 기본 NACL은 모두 허용, 새로 만든 사용자 지정 NACL은 모두 거부다.
- 관리형 프리픽스 리스트(예: CloudFront 오리진 대역)를 SG에서 참조하면 IP 목록 관리가 사라진다.

[헷갈리는 개념 → 필터링 계층](confusions.md#filtering-layer)

### AWS Network Firewall {#network-firewall}

**VPC용 관리형 상태 저장/비저장 방화벽·IPS다. Suricata 호환 규칙과 도메인(FQDN/SNI) 필터를 지원한다.**

- 방화벽 엔드포인트를 전용 서브넷에 두고 라우팅으로 트래픽을 보낸다(IGW 인그레스 라우팅 포함).
- **배포 모델**: 분산(VPC마다 방화벽), 중앙(TGW + 검사 VPC). 중앙 모델은 [어플라이언스 모드](#tgw-appliance-mode)가 필요하다.
- **HOME_NET** 변수는 기본이 방화벽이 있는 VPC CIDR이다. 중앙 모델에서는 스포크 CIDR을 포함하도록 늘려야 규칙이 맞게 동작한다.
- **엄격한 규칙 순서(strict order)**: 지정한 우선순위대로 평가하고 기본 동작(drop 등)을 정한다.
- 로그: 알림 로그·흐름 로그를 S3, CloudWatch Logs, Firehose로 보낸다.
- 정책은 Firewall Manager로 조직 전체에 배포할 수 있다.

[헷갈리는 개념 → 검사 삽입 방식](confusions.md#inspection-insertion) · [필터링 계층](confusions.md#filtering-layer)

### TGW 어플라이언스 모드 {#tgw-appliance-mode}

**TGW가 한 흐름의 양방향 트래픽을 검사 VPC의 같은 AZ 어플라이언스로 보내도록 고정하는 VPC 어태치먼트 옵션이다.**

- 기본 TGW는 트래픽이 들어온 AZ를 유지하려 해서, 출발지와 목적지 AZ가 다르면 요청과 응답이 다른 AZ 방화벽을 지난다 → 상태 저장 방화벽이 응답을 버린다(비대칭 라우팅).
- **검사 VPC 어태치먼트에서** 켠다(스포크가 아니다).
- 증상: AZ가 다른 VPC 사이 통신만 간헐적으로 끊긴다.
- [GWLB](#gwlb)나 [Network Firewall](#network-firewall)을 중앙 검사 VPC에 둘 때 함께 쓴다.

[헷갈리는 개념 → 검사 삽입 방식](confusions.md#inspection-insertion)

### Direct Connect MACsec {#macsec}

**고객 라우터와 DX 장비 사이 크로스 커넥트 구간을 L2(IEEE 802.1AE)로 암호화하는 기능이다.**

- **10/100/400Gbps 전용 연결**(MACsec 지원 포트, 일부 로케이션)과 그 LAG에서만 쓸 수 있다. **호스티드 연결은 지원하지 않는다**(1Gbps도 대상이 아니다).
- 키: 고객이 만든 **CKN/CAK** 쌍(256비트)을 연결이나 LAG에 연결(associate)한다. AWS는 이를 **Secrets Manager** 에 저장한다. 고정 CAK 모드만 지원한다.
- **암호화 모드**: `should_encrypt`(협상 실패 시 비암호화 허용, 기본값), `must_encrypt`(실패 시 트래픽 차단).
- 구현 순서: 키 연결 → 고객 라우터에 같은 키 설정 → 암호화 모드 설정.
- 점대점 구간 암호화라 종단 간 암호화는 아니다. 종단 간이 필요하면 [DX 위 VPN](#vpn-over-dx)이다.

[헷갈리는 개념 → DX 암호화](confusions.md#dx-encryption)

### DX 위 IPsec VPN {#vpn-over-dx}

**DX 전용 회선 위에 Site-to-Site VPN을 얹어 IP 계층(L3)에서 종단 간 암호화하는 구성이다.**

- **퍼블릭 VIF 방식**: 퍼블릭 VIF로 AWS VPN 퍼블릭 엔드포인트에 닿고, 그 위로 VGW/TGW VPN을 맺는다.
- **프라이빗 IP VPN 방식**: [트랜짓 VIF](#transit-vif)를 거쳐 TGW의 사설 IP 주소로 VPN을 맺는다. 퍼블릭 IP가 필요 없다.
- MACsec을 쓸 수 없는 연결(1Gbps, 호스티드)이나 "네트워크 계층 암호화" 요구에 맞는다.
- VPN 터널당 처리량 제한(1.25Gbps)이 그대로 적용되므로 대역폭이 크면 ECMP로 여러 터널을 묶는다.

[헷갈리는 개념 → DX 암호화](confusions.md#dx-encryption)

### 로드 밸런서 TLS·인증서 {#elb-tls}

**ACM 인증서와 ALB/NLB 리스너로 TLS를 종료하거나 통과시키는 설계다.**

- **ACM 인증서는 리전 리소스** 다. ALB/NLB는 같은 리전, **CloudFront는 us-east-1** 의 인증서를 쓴다.
- 외부 CA 인증서는 ACM으로 가져온다(갱신은 직접). 사설 인증서는 **AWS Private CA** 로 발급한다.
- **TLS 종료**: ALB HTTPS 리스너, NLB TLS 리스너. **패스스루**: NLB TCP 리스너(대상이 인증서를 갖는다, 상호 TLS를 대상에서 처리).
- **보안 정책** 으로 TLS 버전과 암호 스위트(전방향 비밀성, FS)를 고른다.
- **엔드 투 엔드 암호화**: 로드 밸런서에서 종료 후 대상으로 다시 HTTPS/TLS로 보낸다.
- SNI로 리스너 하나에 여러 인증서를 붙인다.

### WAF·Shield·Firewall Manager·DNS Firewall {#perimeter-protection}

**웹 계층(L7)과 DNS 계층에서 경계를 보호하는 관리형 서비스 묶음이다.**

- **AWS WAF**: CloudFront, ALB, API Gateway 등에 웹 ACL을 붙인다(SQLi, XSS, 속도 기반 규칙). 로그는 Kinesis Data Firehose, S3, CloudWatch Logs로 보낸다.
- **Shield Advanced**: L3/L4/L7 DDoS 보호, 대응팀(SRT) 지원, DDoS로 늘어난 비용 보호.
- **Firewall Manager**: Organizations 전체에 WAF, Shield, SG, Network Firewall, DNS Firewall 정책을 강제한다. Organizations, 관리자 계정, **AWS Config** 가 전제다.
- **Route 53 Resolver DNS Firewall**: VPC의 DNS 질의를 도메인 목록으로 차단·허용한다. 장애 시 동작을 **fail-open/fail-closed** 로 정한다(가용성 우선이면 fail-open).

[헷갈리는 개념 → 필터링 계층](confusions.md#filtering-layer)
