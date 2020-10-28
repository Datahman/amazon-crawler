interface RootObject {
    remaining_requests: number;
    original_status: number;
    pc_status: number;
    url: string;
    body: Body;
  }
  
  interface Body {
    products: Product[];
    resultInfo: string;
    pagination: Pagination;
  }
  
  interface Pagination {
    currentPage: number;
    nextPage: number;
    totalPages: number;
  }
  
  interface Product {
    name: string;
    price: string;
    customerReview: string;
    customerReviewCount: number;
    shippingMessage: string;
    asin: string;
    image: string;
    url: string;
    isPrime: boolean;
    sponsoredAd: boolean;
    couponInfo: string;
    badgesInfo: string[];
  }